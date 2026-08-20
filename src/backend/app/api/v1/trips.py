from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from ...api.deps import get_current_user, get_db
from ...models.user import User
from ...models.workspace import Workspace
from ...schemas.trips import (
    CheckDuplicateRequest,
    CheckDuplicateResponse,
    RestoreVersionResponse,
    SaveItineraryRequest,
    TripResponse,
    VersionSummary,
)
from ...services import itinerary_service

router = APIRouter()


@router.post("/check-duplicates", response_model=CheckDuplicateResponse)
def check_duplicates(
    req: CheckDuplicateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """UC 2.16 (Tối ưu SQL): Kiểm tra trùng lặp điểm đến và thời gian đè lặp trực tiếp từ CSDL (Không N+1)."""
    dest_cleaned = req.destination.strip().lower()

    # Truy vấn trực tiếp bằng SQL filter
    matching_workspaces = (
        db.query(Workspace)
        .filter(
            Workspace.owner_id == current_user.id,
            or_(
                func.lower(Workspace.destination) == dest_cleaned,
                and_(Workspace.start_date <= req.end_date, Workspace.end_date >= req.start_date),
            ),
        )
        .all()
    )

    dup_dest = False
    overlap_dates = False
    warnings: list[str] = []

    for ws in matching_workspaces:
        is_same_dest = ws.destination and ws.destination.strip().lower() == dest_cleaned
        is_overlap = ws.start_date and ws.end_date and (req.start_date <= ws.end_date and req.end_date >= ws.start_date)

        if is_same_dest:
            dup_dest = True
            warnings.append(f"Bạn đã có chuyến đi '{ws.title}' đến cùng địa điểm '{req.destination}'.")

        if is_overlap:
            overlap_dates = True
            warnings.append(
                f"Thời gian ({req.start_date} -> {req.end_date}) trùng lặp với chuyến đi '{ws.title}' ({ws.start_date} -> {ws.end_date})."
            )

    has_duplicate = dup_dest or overlap_dates
    return {
        "has_duplicate": has_duplicate,
        "duplicate_destination": dup_dest,
        "overlapping_dates": overlap_dates,
        "warnings": warnings,
        "matching_trips": matching_workspaces,
    }


@router.post("/save-itinerary", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def save_itinerary(
    req: SaveItineraryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Workspace:
    """UC 2.13: Lưu bản nháp AI thành chuyến đi Planned, gán Owner, ghi nhận CSDL thực tế (days & activities) & snapshot v1."""
    ws_id = req.workspace_id or req.trip_id
    now_str = datetime.now(timezone.utc).isoformat()

    snapshot_v1 = {
        "version": 1,
        "created_at": now_str,
        "itinerary_data": req.itinerary_data,
    }

    if ws_id:
        ws = db.query(Workspace).filter(Workspace.id == ws_id).first()
        if not ws:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        ws.owner_id = current_user.id
        ws.title = req.title
        ws.destination = req.destination
        ws.start_date = req.start_date
        ws.end_date = req.end_date
        ws.status = "Planned"
        existing_snaps = ws.snapshots
        existing_snaps.append(snapshot_v1)
        ws.set_snapshots(existing_snaps)
    else:
        ws = Workspace(
            owner_id=current_user.id,
            title=req.title,
            destination=req.destination,
            start_date=req.start_date,
            end_date=req.end_date,
            status="Planned",
        )
        ws.set_snapshots([snapshot_v1])
        db.add(ws)

    db.commit()
    db.refresh(ws)

    # Ghi nhận dữ liệu thực tế vào itinerary_days và itinerary_activities qua service
    days_data = req.itinerary_data.get("days", [])
    if isinstance(req.itinerary_data, dict) and "activities" in req.itinerary_data and not days_data:
        # Tự động đóng gói thành ngày 1 nếu itinerary_data chỉ chứa danh sách activities phẳng
        days_data = [{"day_index": 1, "title": "Ngày 1", "activities": req.itinerary_data.get("activities", [])}]

    if days_data:
        itinerary_service._persist_generated_itinerary(
            db, workspace_id=ws.id, days_data=days_data, keep_manual=False
        )

    return ws


@router.get("/history", response_model=list[TripResponse])
def get_trip_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Workspace]:
    """UC 2.17: Trả về danh sách chuyến đi của user từ bảng workspaces (sắp xếp mới nhất)."""
    return db.query(Workspace).filter(Workspace.owner_id == current_user.id).order_by(Workspace.created_at.desc()).all()


@router.get("/{trip_id}/versions", response_model=list[VersionSummary])
def get_trip_versions(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """UC 2.17: Trả về danh sách các version từ history_snapshots của Workspace."""
    ws = db.query(Workspace).filter(Workspace.id == trip_id).first()
    if not ws:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    snapshots = ws.snapshots
    version_list = []
    for snap in snapshots:
        itinerary = snap.get("itinerary_data", {})
        item_count = len(itinerary.get("activities", [])) if isinstance(itinerary, dict) else None
        version_list.append(
            {
                "version": snap.get("version", 1),
                "created_at": snap.get("created_at", ""),
                "item_count": item_count,
            }
        )
    return version_list


@router.post("/{trip_id}/versions/{version_number}/restore", response_model=RestoreVersionResponse)
def restore_trip_version(
    trip_id: int,
    version_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """UC 2.17: Khôi phục data lịch trình từ JSON snapshot và tái lập dữ liệu trong CSDL."""
    ws = db.query(Workspace).filter(Workspace.id == trip_id).first()
    if not ws:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    snapshots = ws.snapshots
    target_snap = next((s for s in snapshots if s.get("version") == version_number), None)
    if not target_snap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found for workspace {trip_id}",
        )

    # Thêm 1 snapshot mới ghi nhận sự kiện khôi phục
    new_version_num = len(snapshots) + 1
    now_str = datetime.now(timezone.utc).isoformat()
    itinerary_data = target_snap.get("itinerary_data", {})

    restored_snap = {
        "version": new_version_num,
        "created_at": now_str,
        "restored_from_version": version_number,
        "itinerary_data": itinerary_data,
    }
    snapshots.append(restored_snap)
    ws.set_snapshots(snapshots)
    db.commit()

    # Tái lập dữ liệu CSDL thực tế
    days_data = itinerary_data.get("days", [])
    if isinstance(itinerary_data, dict) and "activities" in itinerary_data and not days_data:
        days_data = [{"day_index": 1, "title": "Ngày 1", "activities": itinerary_data.get("activities", [])}]

    if days_data:
        itinerary_service._persist_generated_itinerary(
            db, workspace_id=ws.id, days_data=days_data, keep_manual=False
        )

    return {
        "message": f"Successfully restored itinerary to version {version_number}",
        "workspace_id": ws.id,
        "restored_version": version_number,
        "current_status": ws.status,
        "itinerary_data": itinerary_data,
    }
