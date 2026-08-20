from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.itinerary import ItineraryActivity, ItineraryDay
from ..models.workspace import Workspace
from ..schemas.workspace import WorkspaceCreate


def create_workspace(db: Session, payload: WorkspaceCreate) -> Workspace:
    """Tạo workspace mới cho một chuyến đi."""
    prefs_str = json.dumps(payload.preferences) if payload.preferences else None
    db_workspace = Workspace(
        title=payload.title,
        destination=payload.destination,
        start_date=payload.start_date,
        end_date=payload.end_date,
        preferences_json=prefs_str,
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace


def get_workspace(db: Session, workspace_id: int) -> Workspace:
    """Lấy thông tin workspace theo ID. Ném 404 nếu không tìm thấy."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws


def list_workspaces(db: Session, skip: int = 0, limit: int = 100) -> list[Workspace]:
    """Danh sách các workspace."""
    return db.query(Workspace).offset(skip).limit(limit).all()


def get_trip_overview(db: Session, workspace_id: int) -> dict[str, Any]:
    """Tổng hợp nhanh thông tin chuyến đi."""
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
