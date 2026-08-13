"""API khởi tạo workspace và lấy tổng quan chuyến đi."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_workspace_member
from app.db.session import get_db
from app.models.user import User
from app.schemas.itinerary import AdjustItineraryRequest, GenerateItineraryRequest, ItineraryPreviewRequest, ItineraryPreviewResponse, ItineraryResponse, ItineraryVersionResponse, SaveItineraryDraftRequest
from app.schemas.workspace import TripOverviewResponse, WorkspaceCreate, WorkspaceResponse
from app.services.itinerary_service import ItineraryService
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("/preview-itinerary", response_model=ItineraryPreviewResponse)
def preview_itinerary(
    payload: ItineraryPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryPreviewResponse:
    """Create a temporary AI draft before the user saves a workspace."""

    return ItineraryService(db).preview_itinerary(payload)


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkspaceResponse]:
    """Liệt kê các chuyến đi riêng tư mà người dùng được tham gia."""

    return WorkspaceService(db).list_user_workspaces(current_user.id)


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkspaceResponse:
    """Tạo workspace mới cho một chuyến đi."""

    service = WorkspaceService(db)
    workspace = service.create_workspace(payload, current_user.id)
    return workspace


@router.post("/{workspace_id}/save-itinerary", response_model=ItineraryResponse)
def save_itinerary_draft(
    workspace_id: str,
    payload: SaveItineraryDraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    service = ItineraryService(db)
    try:
        require_workspace_member(db, workspace_id, current_user.id)
        return service.save_itinerary_draft(workspace_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc



@router.get("/{workspace_id}/overview", response_model=TripOverviewResponse)
def get_trip_overview(workspace_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TripOverviewResponse:
    """Lấy tổng quan chuyến đi phục vụ UI 5A/5B."""

    service = WorkspaceService(db)
    try:
        require_workspace_member(db, workspace_id, current_user.id)
        return service.get_trip_overview(workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{workspace_id}/generate-itinerary", response_model=ItineraryResponse)
def generate_itinerary(
    workspace_id: str,
    payload: GenerateItineraryRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    """Sinh lịch trình tự động qua GenAI."""

    service = ItineraryService(db)
    try:
        require_workspace_member(db, workspace_id, current_user.id)
        return service.generate_itinerary_draft(workspace_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{workspace_id}/initialize-blank-itinerary", response_model=ItineraryResponse)
def initialize_blank_itinerary(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    """Khởi tạo các ngày trống để người dùng tự lập kế hoạch khi AI không khả dụng."""

    service = ItineraryService(db)
    try:
        require_workspace_member(db, workspace_id, current_user.id)
        return service.initialize_blank_itinerary(workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{workspace_id}/itinerary", response_model=ItineraryResponse)
def get_itinerary(workspace_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ItineraryResponse:
    """Xem lịch trình đúng theo đường dẫn UI yêu cầu."""

    service = ItineraryService(db)
    try:
        require_workspace_member(db, workspace_id, current_user.id)
        return service.get_itinerary(workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{workspace_id}/itinerary-versions", response_model=list[ItineraryVersionResponse])
def list_itinerary_versions(workspace_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[ItineraryVersionResponse]:
    service = ItineraryService(db)
    require_workspace_member(db, workspace_id, current_user.id)
    return service.list_versions(workspace_id)


@router.post("/{workspace_id}/itinerary-versions/{version_id}/restore", response_model=ItineraryResponse)
def restore_itinerary_version(workspace_id: str, version_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ItineraryResponse:
    service = ItineraryService(db)
    try:
        require_workspace_member(db, workspace_id, current_user.id)
        return service.restore_version(workspace_id, version_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{workspace_id}/adjust-itinerary", response_model=ItineraryResponse)
def adjust_itinerary(
    workspace_id: str,
    payload: AdjustItineraryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItineraryResponse:
    """Điều chỉnh lịch trình bằng yêu cầu tiếng Việt tự nhiên."""

    service = ItineraryService(db)
    try:
        require_workspace_member(db, workspace_id, current_user.id)
        return service.adjust_itinerary(workspace_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
