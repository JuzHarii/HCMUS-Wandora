from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1)


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | str
    workspace_id: int | str
    role: str = "user"
    sender_role: str = "user"
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    workspace_id: int | str
    messages: list[ChatMessageResponse] = Field(default_factory=list)
