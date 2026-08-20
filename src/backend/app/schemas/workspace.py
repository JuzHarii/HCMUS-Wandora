import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer, field_validator


class WorkspaceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)


class WorkspaceResponse(BaseModel):
    id: int
    title: str
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None

    model_config = {"from_attributes": True}

    @field_validator("preferences", mode="before")
    @classmethod
    def parse_preferences(cls, v: Any) -> dict[str, Any]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        if isinstance(v, dict):
            return v
        return {}


class TripOverviewResponse(BaseModel):
    workspace_id: int
    title: str
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    total_days: int = 0
    total_activities: int = 0

    model_config = {"from_attributes": True}
