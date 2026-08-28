from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.itinerary import (
    ItineraryActivityCreate,
    ItineraryActivityResponse,
    ItineraryActivityUpdate,
    ItineraryResponse,
)
from app.services import itinerary_service
from app.services.itinerary_service import ItineraryService

router = APIRouter()


@router.get("/{workspace_id}", response_model=ItineraryResponse)
def get_workspace_itinerary(workspace_id: Any, db: Session = Depends(get_db)) -> ItineraryResponse:
    service = ItineraryService(db)
    try:
        return service.get_itinerary(workspace_id)
    except Exception:
        result = itinerary_service.get_itinerary(db, workspace_id)
        return ItineraryResponse.model_validate(result)


@router.post("/activities", response_model=ItineraryActivityResponse, status_code=status.HTTP_201_CREATED)
def add_activity(payload: ItineraryActivityCreate, db: Session = Depends(get_db)) -> ItineraryActivityResponse:
    act = itinerary_service.add_activity(db, payload)
    return ItineraryActivityResponse.model_validate(act)


@router.put("/activities/{activity_id}", response_model=ItineraryActivityResponse)
def update_activity(
    activity_id: Any, payload: ItineraryActivityUpdate, db: Session = Depends(get_db)
) -> ItineraryActivityResponse:
    act = itinerary_service.update_activity(db, activity_id, payload)
    return ItineraryActivityResponse.model_validate(act)
