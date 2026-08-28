from __future__ import annotations

from datetime import date, datetime, time, timedelta
import json
from typing import Any

from fastapi import HTTPException
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
    ItineraryActivityCreate,
    ItineraryActivityUpdate,
    ItineraryDayResponse,
    ItineraryPreviewRequest,
    ItineraryPreviewResponse,
    ItineraryResponse,
    ItineraryVersionResponse,
    SaveItineraryDraftRequest,
    format_time_safe,
    parse_time_safe,
)
from app.services import ai_service
from app.services.ai_service import AIService


def parse_date_safe(val: Any) -> date | None:
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return date.fromisoformat(val)
        except Exception:
            return None
    return None


def get_itinerary(db: Session, workspace_id: Any) -> dict[str, Any]:
    ws_id_val = int(workspace_id) if str(workspace_id).isdigit() else workspace_id
    ws = db.query(Workspace).filter(Workspace.id == ws_id_val).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace không tồn tại")

    days = (
        db.query(ItineraryDay)
        .filter(ItineraryDay.workspace_id == ws_id_val)
        .order_by(ItineraryDay.day_index.asc())
        .all()
    )

    return {"workspace_id": ws.id, "days": days}


def _persist_generated_itinerary(
    db: Session,
    workspace_id: Any,
    days_data: list[dict[str, Any]],
    keep_manual: bool = True,
) -> dict[str, Any]:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace không tồn tại")

    ws.status = "Planned"

    try:
        if keep_manual:
            existing_days = db.query(ItineraryDay).filter(ItineraryDay.workspace_id == workspace_id).all()
            for day in existing_days:
                db.query(ItineraryActivity).filter(
                    ItineraryActivity.day_id == day.id, ItineraryActivity.is_manual == False
                ).delete(synchronize_session=False)
        else:
            db.query(ItineraryDay).filter(ItineraryDay.workspace_id == workspace_id).delete(synchronize_session=False)

        for d_data in days_data:
            day_idx = d_data.get("day_index", 1)
            day_title = d_data.get("title", f"Ngày {day_idx}")

            date_val = parse_date_safe(d_data.get("date_value") or d_data.get("travel_date"))
            if not date_val and ws.start_date:
                date_val = ws.start_date + timedelta(days=day_idx - 1)

            day_obj = (
                db.query(ItineraryDay)
                .filter(ItineraryDay.workspace_id == workspace_id, ItineraryDay.day_index == day_idx)
                .first()
            )
            if not day_obj:
                day_obj = ItineraryDay(
                    workspace_id=workspace_id,
                    day_index=day_idx,
                    date_value=date_val,
                    travel_date=date_val,
                    title=day_title,
                )
                db.add(day_obj)
                db.flush()

            activities_list = d_data.get("activities", [])
            for idx, act_data in enumerate(activities_list, start=1):
                s_time = parse_time_safe(act_data.get("start_time"))
                e_time = parse_time_safe(act_data.get("end_time"))
                order_idx = act_data.get("order_index", act_data.get("sort_order", idx))

                act_obj = ItineraryActivity(
                    day_id=day_obj.id,
                    title=act_data.get("title", "Hoạt động"),
                    start_time=s_time,
                    end_time=e_time,
                    location_name=act_data.get("location_name"),
                    activity_type=act_data.get("activity_type"),
                    notes=act_data.get("notes"),
                    external_url=act_data.get("external_url"),
                    is_manual=False,
                    order_index=order_idx,
                    sort_order=order_idx,
                )
                db.add(act_obj)

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu lịch trình vào CSDL: {str(e)}") from e

    return get_itinerary(db, workspace_id)


async def generate_itinerary_draft(db: Session, workspace_id: Any, force_regenerate: bool = False) -> dict[str, Any]:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace không tồn tại")

    existing_days = db.query(ItineraryDay).filter(ItineraryDay.workspace_id == workspace_id).all()
    if existing_days and not force_regenerate:
        return get_itinerary(db, workspace_id)

    preferences = json.loads(ws.preferences_json) if ws.preferences_json else {}

    days_data = await ai_service.generate_itinerary_draft(
        destination=ws.destination,
        start_date=ws.start_date,
        end_date=ws.end_date,
        preferences=preferences,
    )

    return _persist_generated_itinerary(db, workspace_id, days_data, keep_manual=True)


async def adjust_itinerary(db: Session, workspace_id: Any, instruction: str) -> dict[str, Any]:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace không tồn tại")

    preferences = json.loads(ws.preferences_json) if ws.preferences_json else {}
    current_itin = get_itinerary(db, workspace_id)
    existing_days_data = []
    for day in current_itin.get("days", []):
        existing_days_data.append({
            "day_index": day.day_index,
            "title": day.title,
            "activities": [
                {
                    "title": act.title,
                    "start_time": format_time_safe(act.start_time),
                    "end_time": format_time_safe(act.end_time),
                    "location_name": act.location_name,
                    "notes": act.notes,
                    "is_manual": act.is_manual,
                }
                for act in day.activities
            ]
        })

    days_data = await ai_service.generate_itinerary_draft(
        destination=ws.destination,
        start_date=ws.start_date,
        end_date=ws.end_date,
        preferences=preferences,
        adjustment_instruction=instruction,
        existing_itinerary=existing_days_data,
    )

    return _persist_generated_itinerary(db, workspace_id, days_data, keep_manual=True)


def add_activity(db: Session, payload: ItineraryActivityCreate) -> ItineraryActivity:
    day_id = payload.day_id

    if not day_id:
        if payload.workspace_id and payload.day_index:
            day_obj = (
                db.query(ItineraryDay)
                .filter(
                    ItineraryDay.workspace_id == payload.workspace_id,
                    ItineraryDay.day_index == payload.day_index,
                )
                .first()
            )
            if not day_obj:
                day_obj = ItineraryDay(
                    workspace_id=payload.workspace_id,
                    day_index=payload.day_index,
                    title=f"Ngày {payload.day_index}",
                )
                db.add(day_obj)
                db.flush()
            day_id = day_obj.id
        else:
            raise HTTPException(status_code=422, detail="Cần cung cấp day_id hoặc bộ (workspace_id, day_index)")

    day_obj = db.query(ItineraryDay).filter(ItineraryDay.id == day_id).first()
    if not day_obj:
        raise HTTPException(status_code=404, detail="Không tìm thấy ngày trong lịch trình (Itinerary Day not found)")

    order_val = payload.order_index or payload.sort_order

    activity = ItineraryActivity(
        day_id=day_id,
        title=payload.title,
        start_time=parse_time_safe(payload.start_time),
        end_time=parse_time_safe(payload.end_time),
        location_name=payload.location_name,
        activity_type=payload.activity_type,
        notes=payload.notes,
        external_url=payload.external_url,
        is_manual=True,
        order_index=order_val,
        sort_order=order_val,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def update_activity(db: Session, activity_id: Any, payload: ItineraryActivityUpdate) -> ItineraryActivity:
    act = db.query(ItineraryActivity).filter(ItineraryActivity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Không tìm thấy hoạt động (Activity not found)")

    if payload.title is not None:
        act.title = payload.title
    if payload.start_time is not None:
        act.start_time = parse_time_safe(payload.start_time)
    if payload.end_time is not None:
        act.end_time = parse_time_safe(payload.end_time)
    if payload.location_name is not None:
        act.location_name = payload.location_name
    if payload.notes is not None:
        act.notes = payload.notes
    if payload.external_url is not None:
        act.external_url = payload.external_url
    if payload.order_index is not None:
        act.order_index = payload.order_index
        act.sort_order = payload.order_index
    elif payload.sort_order is not None:
        act.order_index = payload.sort_order
        act.sort_order = payload.sort_order

    db.commit()
    db.refresh(act)
    return act


class ItineraryService:
    """Tập hợp nghiệp vụ liên quan đến lịch trình chuyến đi."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.ai_service = AIService()

    def _get_workspace(self, workspace_id: Any) -> Workspace:
        workspace = self.db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if workspace is None:
            raise ValueError("Workspace không tồn tại.")
        return workspace

    def generate_itinerary_draft(self, workspace_id: Any, request: GenerateItineraryRequest | None = None) -> ItineraryResponse:
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

    def preview_itinerary(self, request: ItineraryPreviewRequest) -> ItineraryPreviewResponse:
        result = self.ai_service.generate_itinerary_draft(request.model_dump())
        return ItineraryPreviewResponse(source=result.source, draft=result.draft)

    def save_itinerary_draft(self, workspace_id: Any, request: SaveItineraryDraftRequest) -> ItineraryResponse:
        workspace = self._get_workspace(workspace_id)
        has_existing_days = self.db.scalar(
            select(func.count(ItineraryDay.id)).where(ItineraryDay.workspace_id == workspace_id)
        ) > 0
        if has_existing_days:
            raise ValueError("This trip already has an itinerary.")
        self._persist_generated_itinerary(workspace_id, request.draft, replace_existing=False)
        self._record_generation(workspace, request.source)
        return self.get_itinerary(workspace_id)

    def initialize_blank_itinerary(self, workspace_id: Any) -> ItineraryResponse:
        workspace = self._get_workspace(workspace_id)
        self._clear_itinerary(workspace_id)
        for day_index, travel_date in enumerate(self._travel_dates(workspace.start_date, workspace.end_date), start=1):
            self.db.add(
                ItineraryDay(
                    workspace_id=workspace_id,
                    day_index=day_index,
                    date_value=travel_date,
                    travel_date=travel_date,
                    title=f"Day {day_index}",
                    summary="Add activities to shape this day.",
                )
            )
        self.db.commit()
        self._record_generation(workspace, "blank")
        return self.get_itinerary(workspace_id)

    def get_itinerary(self, workspace_id: Any) -> ItineraryResponse:
        ws_id_val = int(workspace_id) if str(workspace_id).isdigit() else workspace_id
        workspace = self._get_workspace(ws_id_val)
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

    def list_versions(self, workspace_id: Any) -> list[ItineraryVersionResponse]:
        self._get_workspace(workspace_id)
        versions = self.db.scalars(
            select(ItineraryVersion)
            .where(ItineraryVersion.workspace_id == workspace_id)
            .order_by(ItineraryVersion.created_at.desc())
            .limit(10)
        ).all()
        return [ItineraryVersionResponse.model_validate(version) for version in versions]

    def restore_version(self, workspace_id: Any, version_id: Any) -> ItineraryResponse:
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
                date_value=day_payload.travel_date,
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
                        start_time=parse_time_safe(activity_payload.start_time),
                        end_time=parse_time_safe(activity_payload.end_time),
                        title=activity_payload.title,
                        location_name=activity_payload.location_name,
                        activity_type=activity_payload.activity_type,
                        notes=activity_payload.notes,
                        external_url=activity_payload.external_url,
                        is_manual=activity_payload.is_manual,
                        order_index=activity_payload.order_index or activity_payload.sort_order,
                        sort_order=activity_payload.sort_order or activity_payload.order_index,
                    )
                )
        self.db.commit()
        self._record_generation(workspace, "restored")
        return self.get_itinerary(workspace_id)

    def add_activity(self, payload: ActivityCreate) -> ActivityResponse:
        day = self.db.get(ItineraryDay, payload.day_id)
        if day is None:
            raise ValueError("Ngày lịch trình không tồn tại.")
        activity = ItineraryActivity(
            day_id=day.id,
            title=payload.title,
            start_time=parse_time_safe(payload.start_time),
            end_time=parse_time_safe(payload.end_time),
            location_name=payload.location_name,
            activity_type=payload.activity_type,
            notes=payload.notes,
            external_url=payload.external_url,
            is_manual=True,
            order_index=payload.order_index or payload.sort_order,
            sort_order=payload.sort_order or payload.order_index,
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return self._to_activity_response(activity)

    def get_activity(self, activity_id: Any) -> ItineraryActivity:
        activity = self.db.get(ItineraryActivity, activity_id)
        if activity is None:
            raise ValueError("Hoạt động không tồn tại.")
        return activity

    def update_activity(self, activity_id: Any, payload: ActivityUpdate) -> ActivityResponse:
        activity = self.get_activity(activity_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            if field in ("start_time", "end_time"):
                value = parse_time_safe(value)
            setattr(activity, field, value)
        self.db.commit()
        self.db.refresh(activity)
        return self._to_activity_response(activity)

    def adjust_itinerary(self, workspace_id: Any, request: AdjustItineraryRequest) -> ItineraryResponse:
        workspace = self._get_workspace(workspace_id)
        result = self.ai_service.generate_itinerary_draft(self._workspace_context(workspace), request.instruction)
        self._persist_generated_itinerary(workspace_id, result.draft, replace_existing=False)
        self._record_generation(workspace, result.source)
        return self.get_itinerary(workspace_id)

    def _persist_generated_itinerary(
        self,
        workspace_id: Any,
        draft: GeneratedItineraryPayload,
        replace_existing: bool,
    ) -> None:
        if replace_existing:
            self._remove_generated_activities(workspace_id, len(draft.days))

        for day_payload in draft.days:
            day = self._get_or_create_day(workspace_id, day_payload.day_index)
            day.title = day_payload.title
            day.summary = day_payload.summary
            day.date_value = day_payload.travel_date
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
                    start_time=parse_time_safe(activity_payload.start_time),
                    end_time=parse_time_safe(activity_payload.end_time),
                    title=activity_payload.title,
                    location_name=activity_payload.location_name,
                    activity_type=activity_payload.activity_type,
                    notes=activity_payload.notes,
                    external_url=activity_payload.external_url,
                    is_manual=False,
                    order_index=sort_order,
                    sort_order=sort_order,
                )
                self.db.add(activity)
        self.db.commit()

    def _record_generation(self, workspace: Workspace, source: str) -> None:
        workspace.status = "Planned"
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

    def _get_or_create_day(self, workspace_id: Any, day_index: int) -> ItineraryDay:
        day = self.db.scalar(
            select(ItineraryDay).where(ItineraryDay.workspace_id == workspace_id, ItineraryDay.day_index == day_index)
        )
        if day is not None:
            return day
        return ItineraryDay(workspace_id=workspace_id, day_index=day_index, title=f"Ngày {day_index}")

    def _clear_itinerary(self, workspace_id: Any) -> None:
        existing_days = self.db.scalars(select(ItineraryDay).where(ItineraryDay.workspace_id == workspace_id)).all()
        for day in existing_days:
            self.db.execute(delete(ItineraryActivity).where(ItineraryActivity.day_id == day.id))
        self.db.execute(delete(ItineraryDay).where(ItineraryDay.workspace_id == workspace_id))
        self.db.commit()

    def _remove_generated_activities(self, workspace_id: Any, expected_day_count: int) -> None:
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
            date_value=day.date_value or day.travel_date,
            travel_date=day.travel_date or day.date_value,
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
            order_index=activity.order_index or activity.sort_order,
            sort_order=activity.sort_order or activity.order_index,
            created_at=activity.created_at,
            updated_at=activity.created_at,
        )
