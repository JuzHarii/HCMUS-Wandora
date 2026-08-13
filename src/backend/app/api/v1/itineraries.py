"""API xem và chỉnh sửa chi tiết lịch trình."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_workspace_member
from app.db.session import get_db
from app.models.itinerary import ItineraryDay
from app.models.user import User
from app.schemas.itinerary import ActivityCreate, ActivityResponse, ActivityUpdate, ItineraryResponse
from app.services.itinerary_service import ItineraryService

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


@router.get("/{workspace_id}", response_model=ItineraryResponse)
def get_itinerary(workspace_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ItineraryResponse:
    """Xem lịch trình dạng timeline và map."""

    service = ItineraryService(db)
    try:
        require_workspace_member(db, workspace_id, current_user.id)
        return service.get_itinerary(workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def add_activity(payload: ActivityCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ActivityResponse:
    """Thêm địa điểm hoặc hoạt động thủ công vào lịch trình."""

    service = ItineraryService(db)
    try:
        day = db.get(ItineraryDay, payload.day_id)
        if day is None:
            raise ValueError("Ngày lịch trình không tồn tại.")
        require_workspace_member(db, day.workspace_id, current_user.id)
        return service.add_activity(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: str,
    payload: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActivityResponse:
    """Cập nhật thông tin chi tiết của một hoạt động."""

    service = ItineraryService(db)
    try:
        activity = service.get_activity(activity_id)
        day = db.get(ItineraryDay, activity.day_id)
        if day is None:
            raise ValueError("Ngày lịch trình không tồn tại.")
        require_workspace_member(db, day.workspace_id, current_user.id)
        return service.update_activity(activity_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
