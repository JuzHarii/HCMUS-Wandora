"""API xem và chỉnh sửa chi tiết lịch trình."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.itinerary import ActivityCreate, ActivityResponse, ActivityUpdate, ItineraryResponse
from app.services.itinerary_service import ItineraryService

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


@router.get("/{workspace_id}", response_model=ItineraryResponse)
def get_itinerary(workspace_id: str, db: Session = Depends(get_db)) -> ItineraryResponse:
    """Xem lịch trình dạng timeline và map."""

    service = ItineraryService(db)
    try:
        return service.get_itinerary(workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def add_activity(payload: ActivityCreate, db: Session = Depends(get_db)) -> ActivityResponse:
    """Thêm địa điểm hoặc hoạt động thủ công vào lịch trình."""

    service = ItineraryService(db)
    try:
        return service.add_activity(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(activity_id: str, payload: ActivityUpdate, db: Session = Depends(get_db)) -> ActivityResponse:
    """Cập nhật thông tin chi tiết của một hoạt động."""

    service = ItineraryService(db)
    try:
        return service.update_activity(activity_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
