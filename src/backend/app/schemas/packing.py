from datetime import datetime

from pydantic import BaseModel, Field


class PackingItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(default=1, ge=1)
    is_shared: bool = False
    note: str | None = None


class PackingItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    quantity: int | None = Field(None, ge=1)
    is_shared: bool | None = None
    note: str | None = None


class PackingAssignmentRequest(BaseModel):
    user_id: str | int
    is_checked: bool = False


class PackingListEntryResponse(BaseModel):
    id: str | int
    packing_item_id: str | int
    user_id: str | int
    user_email: str | None = None
    user_full_name: str | None = None
    is_checked: bool

    model_config = {"from_attributes": True}


class PackingItemResponse(BaseModel):
    id: str | int
    workspace_id: str | int
    name: str
    quantity: int
    is_shared: bool
    note: str | None = None
    created_at: datetime
    assignments: list[PackingListEntryResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class PackingSuggestionResult(BaseModel):
    items: list[PackingItemResponse]
    is_fallback: bool
