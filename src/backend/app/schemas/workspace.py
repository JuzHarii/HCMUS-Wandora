import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class WorkspaceBase(BaseModel):
    title: str = Field(min_length=1)
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    budget: int | None = Field(default=None, ge=0)
    travel_style: str | None = None
    group_size: int | None = Field(default=None, ge=1)
    notes: str | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_travel_dates(self) -> "WorkspaceBase":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("Ngày kết thúc phải sau hoặc bằng ngày bắt đầu.")
        return self


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | str
    title: str
    status: str = "Draft"
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    budget: int | None = None
    travel_style: str | None = None
    group_size: int | None = None
    notes: str | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)
    itinerary_source: str | None = None
    itinerary_generated_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

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


class WorkspaceDestinationPayload(BaseModel):
    destination_name: str
    order_index: int = 0


class TripOverviewResponse(BaseModel):
    workspace_id: int | str | None = None
    title: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    total_days: int = 0
    total_activities: int = 0
    workspace: WorkspaceResponse | None = None
    destinations: list[WorkspaceDestinationPayload] = Field(default_factory=list)
    itinerary_days: int = 0
    itinerary_activities: int = 0
    manual_activities: int = 0

    model_config = ConfigDict(from_attributes=True)
