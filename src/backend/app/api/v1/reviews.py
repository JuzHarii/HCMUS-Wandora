from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.review import PlaceReviewCreate, PlaceReviewResponse
from app.services import review_service

router = APIRouter()


@router.post(
    "/workspaces/{workspace_id}/reviews",
    response_model=PlaceReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_or_update_review(
    workspace_id: str,
    payload: PlaceReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlaceReviewResponse:
    """Tạo mới hoặc cập nhật đánh giá / nhận xét địa điểm."""
    res = review_service.create_or_update_review(db, workspace_id, payload, user_id=current_user.id)
    return PlaceReviewResponse.model_validate(res)


@router.get("/workspaces/{workspace_id}/reviews", response_model=list[PlaceReviewResponse])
async def list_workspace_reviews(
    workspace_id: str,
    place_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PlaceReviewResponse]:
    """Lấy danh sách các đánh giá địa điểm trong workspace (có thể lọc theo place_name)."""
    res = review_service.list_workspace_reviews(db, workspace_id, place_name=place_name)
    return [PlaceReviewResponse.model_validate(r) for r in res]
