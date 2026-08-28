from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.itinerary import ItineraryActivity, ItineraryDay
from app.models.user import WorkspaceMember
from app.models.workspace import Workspace, WorkspaceDestination
from app.schemas.workspace import TripOverviewResponse, WorkspaceCreate


def create_workspace(db: Session, payload: WorkspaceCreate, owner_id: Any = None) -> Workspace:
    prefs_str = json.dumps(payload.preferences) if payload.preferences else None
    db_workspace = Workspace(
        title=payload.title,
        destination=payload.destination,
        start_date=payload.start_date,
        end_date=payload.end_date,
        budget=payload.budget,
        travel_style=payload.travel_style,
        group_size=payload.group_size,
        notes=payload.notes,
        preferences_json=prefs_str,
        owner_id=owner_id,
    )
    db.add(db_workspace)
    db.flush()

    if payload.destination:
        dest_obj = WorkspaceDestination(
            workspace_id=db_workspace.id,
            destination_name=payload.destination,
            name=payload.destination,
            order_index=0,
        )
        db.add(dest_obj)

    if owner_id:
        db.add(WorkspaceMember(workspace_id=db_workspace.id, user_id=owner_id, role="owner", is_owner=True))

    db.commit()
    db.refresh(db_workspace)
    return db_workspace


def get_workspace(db: Session, workspace_id: Any) -> Workspace:
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


def list_workspaces(db: Session, skip: int = 0, limit: int = 100) -> list[Workspace]:
    return db.query(Workspace).offset(skip).limit(limit).all()


def get_trip_overview(db: Session, workspace_id: Any) -> dict[str, Any]:
    ws = get_workspace(db, workspace_id)

    total_days = db.query(ItineraryDay).filter(ItineraryDay.workspace_id == workspace_id).count()

    total_activities = (
        db.query(func.count(ItineraryActivity.id))
        .join(ItineraryDay, ItineraryActivity.day_id == ItineraryDay.id)
        .filter(ItineraryDay.workspace_id == workspace_id)
        .scalar()
        or 0
    )

    if total_days == 0 and ws.start_date and ws.end_date:
        total_days = (ws.end_date - ws.start_date).days + 1
        if total_days < 0:
            total_days = 0

    return {
        "workspace_id": ws.id,
        "title": ws.title,
        "destination": ws.destination,
        "start_date": ws.start_date,
        "end_date": ws.end_date,
        "total_days": total_days,
        "total_activities": total_activities,
    }


class WorkspaceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_workspace(self, payload: WorkspaceCreate, owner_id: Any) -> Workspace:
        return create_workspace(self.db, payload, owner_id=owner_id)

    def list_user_workspaces(self, user_id: Any) -> list[Workspace]:
        return self.db.scalars(
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at.desc())
        ).all()

    def get_workspace(self, workspace_id: Any) -> Workspace:
        return get_workspace(self.db, workspace_id)

    def get_trip_overview(self, workspace_id: Any) -> TripOverviewResponse:
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
            workspace_id=workspace.id,
            title=workspace.title,
            destination=workspace.destination,
            start_date=workspace.start_date,
            end_date=workspace.end_date,
            total_days=itinerary_days,
            total_activities=itinerary_activities,
            workspace=workspace,
            destinations=[
                {
                    "destination_name": item.destination_name or item.name or "",
                    "order_index": item.order_index,
                }
                for item in destinations
            ],
            itinerary_days=itinerary_days,
            itinerary_activities=itinerary_activities,
            manual_activities=manual_activities,
        )
