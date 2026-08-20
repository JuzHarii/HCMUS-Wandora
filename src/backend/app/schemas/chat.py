from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    id: int
    workspace_id: int
    sender_role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    workspace_id: int
    messages: list[ChatMessageResponse] = Field(default_factory=list)
