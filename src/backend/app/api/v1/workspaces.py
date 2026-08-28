from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.itinerary import (
    AdjustItineraryRequest,
    GenerateItineraryRequest,
    ItineraryPreviewRequest,
    ItineraryPreviewResponse,
    ItineraryResponse,
    ItineraryVersionResponse,
    SaveItineraryDraftRequest,
)
from app.schemas.workspace import TripOverviewResponse, WorkspaceCreate, WorkspaceResponse
from app.services import itinerary_service, workspace_service
from app.services.itinerary_service import ItineraryService
from app.services.workspace_service import WorkspaceService

router = APIRouter()


@router.post("/preview-itinerary", response_model=ItineraryPreviewResponse)
def preview_itinerary(
    payload: ItineraryPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryPreviewResponse:
    return ItineraryService(db).preview_itinerary(payload)


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceResponse:
    ws = workspace_service.create_workspace(db, payload, owner_id=current_user.id)
    return WorkspaceResponse.model_validate(ws)


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkspaceResponse]:
    workspaces = WorkspaceService(db).list_user_workspaces(current_user.id)
    return [WorkspaceResponse.model_validate(ws) for ws in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: Any,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceResponse:
    ws = workspace_service.get_workspace(db, workspace_id)
    return WorkspaceResponse.model_validate(ws)


@router.get("/{workspace_id}/overview", response_model=TripOverviewResponse)
def get_trip_overview(
    workspace_id: Any,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TripOverviewResponse:
    overview = workspace_service.get_trip_overview(db, workspace_id)
    return TripOverviewResponse.model_validate(overview)


@router.post("/{workspace_id}/generate-itinerary", response_model=ItineraryResponse)
async def generate_itinerary(
    workspace_id: Any,
    payload: GenerateItineraryRequest = GenerateItineraryRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    result = await itinerary_service.generate_itinerary_draft(
        db, workspace_id, force_regenerate=payload.force_regenerate
    )
    return ItineraryResponse.model_validate(result)


@router.post("/{workspace_id}/initialize-blank-itinerary", response_model=ItineraryResponse)
def initialize_blank_itinerary(
    workspace_id: Any,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    return ItineraryService(db).initialize_blank_itinerary(workspace_id)


@router.get("/{workspace_id}/itinerary", response_model=ItineraryResponse)
def get_workspace_itinerary(
    workspace_id: Any,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    result = itinerary_service.get_itinerary(db, workspace_id)
    return ItineraryResponse.model_validate(result)


@router.post("/{workspace_id}/save-itinerary", response_model=ItineraryResponse)
def save_itinerary_draft(
    workspace_id: Any,
    payload: SaveItineraryDraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    return ItineraryService(db).save_itinerary_draft(workspace_id, payload)


@router.get("/{workspace_id}/itinerary-versions", response_model=list[ItineraryVersionResponse])
def list_itinerary_versions(
    workspace_id: Any,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ItineraryVersionResponse]:
    return ItineraryService(db).list_versions(workspace_id)


@router.post("/{workspace_id}/itinerary-versions/{version_id}/restore", response_model=ItineraryResponse)
def restore_itinerary_version(
    workspace_id: Any,
    version_id: Any,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    return ItineraryService(db).restore_version(workspace_id, version_id)


@router.post("/{workspace_id}/adjust-itinerary", response_model=ItineraryResponse)
async def adjust_itinerary(
    workspace_id: Any,
    payload: AdjustItineraryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    result = await itinerary_service.adjust_itinerary(db, workspace_id, instruction=payload.instruction)
    return ItineraryResponse.model_validate(result)
