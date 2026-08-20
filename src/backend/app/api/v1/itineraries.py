from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.itinerary import (
    ItineraryActivityCreate,
    ItineraryActivityResponse,
    ItineraryActivityUpdate,
    ItineraryResponse,
)
from ...services import itinerary_service

router = APIRouter()


@router.get("/{workspace_id}", response_model=ItineraryResponse)
async def get_workspace_itinerary(workspace_id: int, db: Session = Depends(get_db)) -> ItineraryResponse:
    """Lấy toàn bộ lịch trình theo workspace."""
    result = itinerary_service.get_itinerary(db, workspace_id)
    return ItineraryResponse.model_validate(result)


@router.post("/activities", response_model=ItineraryActivityResponse, status_code=status.HTTP_201_CREATED)
async def add_activity(payload: ItineraryActivityCreate, db: Session = Depends(get_db)) -> ItineraryActivityResponse:
    """Thêm hoạt động mới vào lịch trình (Cưỡng chế is_manual=True)."""
    act = itinerary_service.add_activity(db, payload)
    return ItineraryActivityResponse.model_validate(act)


@router.put("/activities/{activity_id}", response_model=ItineraryActivityResponse)
async def update_activity(
    activity_id: int, payload: ItineraryActivityUpdate, db: Session = Depends(get_db)
) -> ItineraryActivityResponse:
    """Cập nhật thông tin của một hoạt động."""
    act = itinerary_service.update_activity(db, activity_id, payload)
    return ItineraryActivityResponse.model_validate(act)
