"""Schemas for the shared packing checklist."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PackingItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(default=1, ge=1, le=99)
    note: str | None = Field(default=None, max_length=1000)
    assigned_to: str | None = Field(default=None, max_length=255)


class PackingItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    quantity: int | None = Field(default=None, ge=1, le=99)
    note: str | None = Field(default=None, max_length=1000)
    assigned_to: str | None = Field(default=None, max_length=255)
    is_completed: bool | None = None


class PackingItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    name: str
    quantity: int
    note: str | None
    assigned_to: str | None
    is_completed: bool
    created_at: datetime
