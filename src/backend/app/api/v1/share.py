from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.itinerary import ItineraryResponse
from app.schemas.share import ShareLinkResponse, TripExportResponse
from app.services import share_service

router = APIRouter()


@router.post(
    "/workspaces/{workspace_id}/share", response_model=ShareLinkResponse, status_code=status.HTTP_201_CREATED
)
async def create_share_link(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShareLinkResponse:
    """Sinh đường dẫn chia sẻ liên kết công khai cho chuyến đi."""
    res = share_service.create_share_link(db, workspace_id)
    return ShareLinkResponse.model_validate(res)


@router.get("/share/{token}", response_model=ItineraryResponse)
async def get_workspace_by_share_token(
    token: str,
    db: Session = Depends(get_db),
) -> ItineraryResponse:
    """Truy cập xem lịch trình qua Token chia sẻ công khai mà không cần tài khoản."""
    res = share_service.get_workspace_by_share_token(db, token)
    return ItineraryResponse.model_validate(res)


@router.get("/workspaces/{workspace_id}/export", response_model=TripExportResponse)
async def export_trip_plan(
    workspace_id: str,
    format: str = Query(default="markdown", description="json hoặc markdown"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TripExportResponse:
    """Xuất kế hoạch chuyến đi ra file JSON hoặc Markdown (Yêu cầu chuyến đi ở trạng thái Planned)."""
    res = share_service.export_trip_plan(db, workspace_id, export_format=format)
    return TripExportResponse.model_validate(res)
