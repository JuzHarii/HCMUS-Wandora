from datetime import datetime

from pydantic import BaseModel, Field


class PlaceReviewCreate(BaseModel):
    place_name: str = Field(..., min_length=1, max_length=255)
    rating: int = Field(..., ge=1, le=5, description="Đánh giá từ 1 đến 5 sao")
    comment: str | None = None
    user_id: int = Field(default=1, description="ID người dùng gửi đánh giá")


class PlaceReviewResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    user_email: str | None = None
    user_full_name: str | None = None
    place_name: str
    rating: int
    comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
