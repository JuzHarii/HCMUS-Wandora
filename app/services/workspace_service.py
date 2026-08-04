"""Nghiệp vụ quản lý workspace và dữ liệu tổng quan."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.itinerary import ItineraryActivity, ItineraryDay
from app.models.workspace import Workspace, WorkspaceDestination
from app.schemas.workspace import TripOverviewResponse, WorkspaceCreate


class WorkspaceService:
    """Tập hợp nghiệp vụ liên quan đến workspace."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_workspace(self, payload: WorkspaceCreate) -> Workspace:
        """Tạo workspace mới từ payload UI."""

        workspace = Workspace(**payload.model_dump())
        self.db.add(workspace)
        self.db.flush()

        destination = WorkspaceDestination(
            workspace_id=workspace.id,
            destination_name=payload.destination,
            order_index=0,
        )
        self.db.add(destination)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def get_workspace(self, workspace_id: str) -> Workspace:
        """Lấy workspace theo định danh."""

        workspace = self.db.get(Workspace, workspace_id)
        if workspace is None:
            raise ValueError("Workspace không tồn tại.")
        return workspace

    def get_trip_overview(self, workspace_id: str) -> TripOverviewResponse:
        """Tổng hợp dữ liệu để hiển thị màn hình 5A/5B."""

        workspace = self.get_workspace(workspace_id)
        destinations = self.db.scalars(
            select(WorkspaceDestination).where(WorkspaceDestination.workspace_id == workspace_id).order_by(WorkspaceDestination.order_index)
        ).all()
        itinerary_days = self.db.scalar(select(func.count(ItineraryDay.id)).where(ItineraryDay.workspace_id == workspace_id)) or 0
        itinerary_activities = self.db.scalar(
            select(func.count(ItineraryActivity.id)).join(ItineraryDay, ItineraryActivity.day_id == ItineraryDay.id).where(ItineraryDay.workspace_id == workspace_id)
        ) or 0
        manual_activities = self.db.scalar(
            select(func.count(ItineraryActivity.id)).join(ItineraryDay, ItineraryActivity.day_id == ItineraryDay.id).where(
                ItineraryDay.workspace_id == workspace_id,
                ItineraryActivity.is_manual.is_(True),
            )
        ) or 0
        return TripOverviewResponse(
            workspace=workspace,
            destinations=[
                {
                    "destination_name": item.destination_name,
                    "order_index": item.order_index,
                }
                for item in destinations
            ],
            itinerary_days=itinerary_days,
            itinerary_activities=itinerary_activities,
            manual_activities=manual_activities,
        )
