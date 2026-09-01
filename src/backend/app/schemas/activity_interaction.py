from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    id: str | int
    activity_id: str | int
    user_id: str | int
    user_name: str | None = None
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VoteCreate(BaseModel):
    vote_value: int = Field(..., description="1 cho Upvote, -1 cho Downvote")


class VoteResponse(BaseModel):
    id: str | int
    activity_id: str | int
    user_id: str | int
    vote_value: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
