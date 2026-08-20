from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from ..models.review import PlaceReview
from ..models.user import User
from ..schemas.review import PlaceReviewCreate
from .workspace_service import get_workspace


def create_or_update_review(db: Session, workspace_id: int, payload: PlaceReviewCreate) -> dict[str, Any]:
    """
    Tạo mới hoặc cập nhật đánh giá / nhận xét địa điểm của người dùng (PA3 2.10).

    Công dụng:
    - Kiểm tra workspace tồn tại.
    - Tìm kiếm xem người dùng đã đánh giá địa điểm này trong workspace chưa (bảo tồn UniqueConstraint).
    - Cập nhật số sao (1-5) và bình luận nếu đã có, hoặc tạo mới nếu chưa có.
    """
    _ = get_workspace(db, workspace_id)

    # Đảm bảo user tồn tại
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        user = User(id=payload.user_id, email=f"user{payload.user_id}@wandora.app", full_name=f"User {payload.user_id}")
        db.add(user)
        db.flush()

    review = (
        db.query(PlaceReview)
        .filter(
            PlaceReview.workspace_id == workspace_id,
            PlaceReview.user_id == payload.user_id,
            PlaceReview.place_name == payload.place_name,
        )
        .first()
    )

    if review:
        review.rating = payload.rating
        review.comment = payload.comment
    else:
        review = PlaceReview(
            workspace_id=workspace_id,
            user_id=payload.user_id,
            place_name=payload.place_name,
            rating=payload.rating,
            comment=payload.comment,
        )
        db.add(review)

    db.commit()
    db.refresh(review)

    return {
        "id": review.id,
        "workspace_id": review.workspace_id,
        "user_id": review.user_id,
        "user_email": user.email if user else None,
        "user_full_name": user.full_name if user else None,
        "place_name": review.place_name,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at,
    }


def list_workspace_reviews(
    db: Session, workspace_id: int, place_name: str | None = None
) -> list[dict[str, Any]]:
    """
    Lấy danh sách đánh giá địa điểm trong workspace (có thể lọc theo tên địa điểm cụ thể).
    """
    _ = get_workspace(db, workspace_id)

    query = db.query(PlaceReview).filter(PlaceReview.workspace_id == workspace_id)
    if place_name:
        query = query.filter(PlaceReview.place_name == place_name)

    reviews = query.order_by(PlaceReview.created_at.desc()).all()

    result = []
    for r in reviews:
        user = db.query(User).filter(User.id == r.user_id).first()
        result.append(
            {
                "id": r.id,
                "workspace_id": r.workspace_id,
                "user_id": r.user_id,
                "user_email": user.email if user else None,
                "user_full_name": user.full_name if user else None,
                "place_name": r.place_name,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at,
            }
        )
    return result
