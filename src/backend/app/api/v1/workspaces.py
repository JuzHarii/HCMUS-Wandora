from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.itinerary import AdjustItineraryRequest, GenerateItineraryRequest, ItineraryResponse
from ...schemas.workspace import TripOverviewResponse, WorkspaceCreate, WorkspaceResponse
from ...services import itinerary_service, workspace_service

router = APIRouter()


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(payload: WorkspaceCreate, db: Session = Depends(get_db)) -> WorkspaceResponse:
    """Tạo workspace mới cho một chuyến đi."""
    ws = workspace_service.create_workspace(db, payload)
    return WorkspaceResponse.model_validate(ws)


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[WorkspaceResponse]:
    """Lấy danh sách các workspace."""
    workspaces = workspace_service.list_workspaces(db, skip=skip, limit=limit)
    return [WorkspaceResponse.model_validate(ws) for ws in workspaces]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: int, db: Session = Depends(get_db)) -> WorkspaceResponse:
    """Lấy thông tin chi tiết một workspace theo ID."""
    ws = workspace_service.get_workspace(db, workspace_id)
    return WorkspaceResponse.model_validate(ws)


@router.get("/{workspace_id}/overview", response_model=TripOverviewResponse)
async def get_trip_overview(workspace_id: int, db: Session = Depends(get_db)) -> TripOverviewResponse:
    """Lấy tổng quan nhanh của workspace."""
    overview = workspace_service.get_trip_overview(db, workspace_id)
    return TripOverviewResponse.model_validate(overview)


@router.post("/{workspace_id}/generate-itinerary", response_model=ItineraryResponse)
async def generate_itinerary(
    workspace_id: int,
    payload: GenerateItineraryRequest = GenerateItineraryRequest(),
    db: Session = Depends(get_db),
) -> ItineraryResponse:
    """Khởi chạy sinh lịch trình cho workspace."""
    result = await itinerary_service.generate_itinerary_draft(
        db, workspace_id, force_regenerate=payload.force_regenerate
    )
    return ItineraryResponse.model_validate(result)


@router.get("/{workspace_id}/itinerary", response_model=ItineraryResponse)
async def get_workspace_itinerary(workspace_id: int, db: Session = Depends(get_db)) -> ItineraryResponse:
    """Lấy lịch trình hiện có của workspace."""
    result = itinerary_service.get_itinerary(db, workspace_id)
    return ItineraryResponse.model_validate(result)


@router.post("/{workspace_id}/adjust-itinerary", response_model=ItineraryResponse)
async def adjust_itinerary(
    workspace_id: int, payload: AdjustItineraryRequest, db: Session = Depends(get_db)
) -> ItineraryResponse:
    """Điều chỉnh lịch trình theo hướng dẫn mới."""
    result = await itinerary_service.adjust_itinerary(db, workspace_id, instruction=payload.instruction)
    return ItineraryResponse.model_validate(result)
