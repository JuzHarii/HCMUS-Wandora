"""Nghiệp vụ sinh, xem và điều chỉnh lịch trình."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.itinerary import ItineraryActivity, ItineraryDay, ItineraryVersion
from app.models.workspace import Workspace
from app.schemas.itinerary import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    AdjustItineraryRequest,
    GenerateItineraryRequest,
    GeneratedItineraryPayload,
    ItineraryDayResponse,
    ItineraryResponse,
    ItineraryVersionResponse,
)
from app.services.ai_service import AIService


class ItineraryService:
    """Tập hợp nghiệp vụ liên quan đến lịch trình chuyến đi."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.ai_service = AIService()

    def _get_workspace(self, workspace_id: str) -> Workspace:
        workspace = self.db.get(Workspace, workspace_id)
        if workspace is None:
            raise ValueError("Workspace không tồn tại.")
        return workspace

    def generate_itinerary_draft(self, workspace_id: str, request: GenerateItineraryRequest | None = None) -> ItineraryResponse:
        """Sinh và lưu bản nháp lịch trình cho workspace."""

        workspace = self._get_workspace(workspace_id)
        has_existing_days = self.db.scalar(
            select(func.count(ItineraryDay.id)).where(ItineraryDay.workspace_id == workspace_id)
        ) > 0
        if has_existing_days and not (request and request.force_regenerate):
            return self.get_itinerary(workspace_id)

        if has_existing_days:
            self._snapshot_current_itinerary(workspace)
        result = self.ai_service.generate_itinerary_draft(self._workspace_context(workspace))
        self._persist_generated_itinerary(workspace_id, result.draft, replace_existing=True)
        self._record_generation(workspace, result.source)
        return self.get_itinerary(workspace_id)

    def initialize_blank_itinerary(self, workspace_id: str) -> ItineraryResponse:
        """Khởi tạo timeline trống khi người dùng không muốn chờ AI tạo bản nháp."""

        workspace = self._get_workspace(workspace_id)
        self._clear_itinerary(workspace_id)
        for day_index, travel_date in enumerate(self._travel_dates(workspace.start_date, workspace.end_date), start=1):
            self.db.add(
                ItineraryDay(
                    workspace_id=workspace_id,
                    day_index=day_index,
                    travel_date=travel_date,
                    title=f"Day {day_index}",
                    summary="Add activities to shape this day.",
                )
            )
        self.db.commit()
        self._record_generation(workspace, "blank")
        return self.get_itinerary(workspace_id)

    def get_itinerary(self, workspace_id: str) -> ItineraryResponse:
        """Lấy toàn bộ lịch trình dưới dạng timeline/map."""

        workspace = self._get_workspace(workspace_id)
        days = self.db.scalars(
            select(ItineraryDay)
            .options(selectinload(ItineraryDay.activities))
            .where(ItineraryDay.workspace_id == workspace.id)
            .order_by(ItineraryDay.day_index)
        ).all()
        return ItineraryResponse(
            workspace_id=workspace.id,
            generation_source=workspace.itinerary_source,
            generated_at=workspace.itinerary_generated_at,
            days=[self._to_day_response(day) for day in days],
        )

    def list_versions(self, workspace_id: str) -> list[ItineraryVersionResponse]:
        self._get_workspace(workspace_id)
        versions = self.db.scalars(
            select(ItineraryVersion)
            .where(ItineraryVersion.workspace_id == workspace_id)
            .order_by(ItineraryVersion.created_at.desc())
            .limit(10)
        ).all()
        return [ItineraryVersionResponse.model_validate(version) for version in versions]

    def restore_version(self, workspace_id: str, version_id: str) -> ItineraryResponse:
        workspace = self._get_workspace(workspace_id)
        version = self.db.get(ItineraryVersion, version_id)
        if version is None or version.workspace_id != workspace_id:
            raise ValueError("Itinerary version does not exist.")
        snapshot = ItineraryResponse.model_validate(version.snapshot)
        self._clear_itinerary(workspace_id)
        for day_payload in snapshot.days:
            day = ItineraryDay(
                workspace_id=workspace_id,
                day_index=day_payload.day_index,
                travel_date=day_payload.travel_date,
                title=day_payload.title,
                summary=day_payload.summary,
            )
            self.db.add(day)
            self.db.flush()
            for activity_payload in day_payload.activities:
                self.db.add(
                    ItineraryActivity(
                        day_id=day.id,
                        start_time=activity_payload.start_time,
                        end_time=activity_payload.end_time,
                        title=activity_payload.title,
                        location_name=activity_payload.location_name,
                        activity_type=activity_payload.activity_type,
                        notes=activity_payload.notes,
                        external_url=activity_payload.external_url,
                        is_manual=activity_payload.is_manual,
                        sort_order=activity_payload.sort_order,
                    )
                )
        self.db.commit()
        self._record_generation(workspace, "restored")
        return self.get_itinerary(workspace_id)

    def add_activity(self, payload: ActivityCreate) -> ActivityResponse:
        """Thêm hoạt động thủ công và đánh dấu is_manual để tránh AI ghi đè."""

        day = self.db.get(ItineraryDay, payload.day_id)
        if day is None:
            raise ValueError("Ngày lịch trình không tồn tại.")
        activity = ItineraryActivity(**payload.model_dump(exclude={"is_manual"}), is_manual=True)
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return self._to_activity_response(activity)

    def get_activity(self, activity_id: str) -> ItineraryActivity:
        activity = self.db.get(ItineraryActivity, activity_id)
        if activity is None:
            raise ValueError("Hoạt động không tồn tại.")
        return activity

    def update_activity(self, activity_id: str, payload: ActivityUpdate) -> ActivityResponse:
        """Cập nhật thời gian, ghi chú hoặc nội dung hoạt động."""

        activity = self.get_activity(activity_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(activity, field, value)
        self.db.commit()
        self.db.refresh(activity)
        return self._to_activity_response(activity)

    def adjust_itinerary(self, workspace_id: str, request: AdjustItineraryRequest) -> ItineraryResponse:
        """Điều chỉnh lịch trình qua câu lệnh tiếng Việt tự nhiên."""

        workspace = self._get_workspace(workspace_id)
        result = self.ai_service.generate_itinerary_draft(self._workspace_context(workspace), request.instruction)
        self._persist_generated_itinerary(workspace_id, result.draft, replace_existing=False)
        self._record_generation(workspace, result.source)
        return self.get_itinerary(workspace_id)

    def _persist_generated_itinerary(
        self,
        workspace_id: str,
        draft: GeneratedItineraryPayload,
        replace_existing: bool,
    ) -> None:
        """Ghi dữ liệu AI sinh ra xuống CSDL."""

        if replace_existing:
            self._remove_generated_activities(workspace_id, len(draft.days))

        for day_payload in draft.days:
            day = self._get_or_create_day(workspace_id, day_payload.day_index)
            day.title = day_payload.title
            day.summary = day_payload.summary
            day.travel_date = day_payload.travel_date
            self.db.add(day)
            self.db.flush()

            if not replace_existing:
                self.db.execute(
                    delete(ItineraryActivity).where(
                        ItineraryActivity.day_id == day.id,
                        ItineraryActivity.is_manual.is_(False),
                    )
                )

            for sort_order, activity_payload in enumerate(day_payload.activities, start=1):
                activity = ItineraryActivity(
                    day_id=day.id,
                    start_time=self._parse_time(activity_payload.start_time),
                    end_time=self._parse_time(activity_payload.end_time),
                    title=activity_payload.title,
                    location_name=activity_payload.location_name,
                    activity_type=activity_payload.activity_type,
                    notes=activity_payload.notes,
                    external_url=activity_payload.external_url,
                    is_manual=False,
                    sort_order=sort_order,
                )
                self.db.add(activity)
        self.db.commit()

    def _record_generation(self, workspace: Workspace, source: str) -> None:
        workspace.status = "Planning"
        workspace.itinerary_source = source
        workspace.itinerary_generated_at = datetime.utcnow()
        self.db.add(workspace)
        self.db.commit()

    def _snapshot_current_itinerary(self, workspace: Workspace) -> None:
        current = self.get_itinerary(workspace.id)
        if not current.days:
            return
        self.db.add(
            ItineraryVersion(
                workspace_id=workspace.id,
                generation_source=workspace.itinerary_source,
                snapshot=current.model_dump(mode="json"),
            )
        )
        self.db.commit()

    def _get_or_create_day(self, workspace_id: str, day_index: int) -> ItineraryDay:
        day = self.db.scalar(
            select(ItineraryDay).where(ItineraryDay.workspace_id == workspace_id, ItineraryDay.day_index == day_index)
        )
        if day is not None:
            return day
        return ItineraryDay(workspace_id=workspace_id, day_index=day_index, title=f"Ngày {day_index}")

    def _clear_itinerary(self, workspace_id: str) -> None:
        existing_days = self.db.scalars(select(ItineraryDay).where(ItineraryDay.workspace_id == workspace_id)).all()
        for day in existing_days:
            self.db.execute(delete(ItineraryActivity).where(ItineraryActivity.day_id == day.id))
        self.db.execute(delete(ItineraryDay).where(ItineraryDay.workspace_id == workspace_id))
        self.db.commit()

    def _remove_generated_activities(self, workspace_id: str, expected_day_count: int) -> None:
        """Refresh generated content while retaining manual activities on matching days."""

        days = self.db.scalars(select(ItineraryDay).where(ItineraryDay.workspace_id == workspace_id)).all()
        for day in days:
            self.db.execute(
                delete(ItineraryActivity).where(
                    ItineraryActivity.day_id == day.id,
                    ItineraryActivity.is_manual.is_(False),
                )
            )
            has_manual_activity = self.db.scalar(
                select(func.count(ItineraryActivity.id)).where(
                    ItineraryActivity.day_id == day.id,
                    ItineraryActivity.is_manual.is_(True),
                )
            ) > 0
            if day.day_index > expected_day_count and not has_manual_activity:
                self.db.delete(day)
        self.db.commit()

    def _travel_dates(self, start_date: date | None, end_date: date | None) -> list[date | None]:
        if start_date is None or end_date is None or end_date < start_date:
            return [None]
        duration = (end_date - start_date).days + 1
        return [start_date + timedelta(days=offset) for offset in range(duration)]

    def _workspace_context(self, workspace: Workspace) -> dict[str, object]:
        """Chuyển workspace sang dict dễ đưa vào prompt."""

        return {
            "id": workspace.id,
            "title": workspace.title,
            "destination": workspace.destination,
            "start_date": workspace.start_date,
            "end_date": workspace.end_date,
            "budget": workspace.budget,
            "travel_style": workspace.travel_style,
            "group_size": workspace.group_size,
            "notes": workspace.notes,
        }

    def _to_day_response(self, day: ItineraryDay) -> ItineraryDayResponse:
        return ItineraryDayResponse(
            id=day.id,
            workspace_id=day.workspace_id,
            day_index=day.day_index,
            travel_date=day.travel_date,
            title=day.title,
            summary=day.summary,
            activities=[self._to_activity_response(activity) for activity in day.activities],
        )

    def _to_activity_response(self, activity: ItineraryActivity) -> ActivityResponse:
        return ActivityResponse(
            id=activity.id,
            day_id=activity.day_id,
            start_time=activity.start_time,
            end_time=activity.end_time,
            title=activity.title,
            location_name=activity.location_name,
            activity_type=activity.activity_type,
            notes=activity.notes,
            external_url=activity.external_url,
            is_manual=activity.is_manual,
            sort_order=activity.sort_order,
            created_at=activity.created_at,
            updated_at=activity.updated_at,
        )

    def _parse_time(self, value: str | None) -> time | None:
        if not value:
            return None
        parts = value.split(":")
        return time(hour=int(parts[0]), minute=int(parts[1]))
