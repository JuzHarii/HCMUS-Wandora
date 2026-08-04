"""Schemas cho hội thoại với trợ lý AI."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageCreate(BaseModel):
    """Payload gửi tin nhắn mới."""

    content: str = Field(min_length=1)


class ChatMessageResponse(BaseModel):
    """Phản hồi cho một tin nhắn hội thoại."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    role: str
    content: str
    created_at: datetime
