from datetime import date, time
from typing import Any

from pydantic import BaseModel, Field, field_serializer, field_validator

from ..core.time_utils import format_time_safe, parse_time_safe


class ItineraryActivityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    start_time: time | str | None = None
    end_time: time | str | None = None
    location_name: str | None = None
    notes: str | None = None
    external_url: str | None = None
    is_manual: bool = False
    order_index: int = 0

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time(cls, v: Any) -> time | None:
        return parse_time_safe(v)


class ItineraryActivityCreate(ItineraryActivityBase):
    day_id: int | None = None
    workspace_id: int | None = None
    day_index: int | None = None
    is_manual: bool = True  # Forced to True for user creation per Sprint 2 requirement


class ItineraryActivityUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    start_time: time | str | None = None
    end_time: time | str | None = None
    location_name: str | None = None
    notes: str | None = None
    external_url: str | None = None
    order_index: int | None = None

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time(cls, v: Any) -> time | None:
        return parse_time_safe(v)


class ItineraryActivityResponse(BaseModel):
    id: int
    day_id: int
    title: str
    start_time: time | str | None = None
    end_time: time | str | None = None
    location_name: str | None = None
    notes: str | None = None
    external_url: str | None = None
    is_manual: bool
    order_index: int

    model_config = {"from_attributes": True}

    @field_serializer("start_time", "end_time")
    def serialize_time(self, v: time | str | None) -> str | None:
        if isinstance(v, time):
            return format_time_safe(v)
        return v


class ItineraryDayResponse(BaseModel):
    id: int
    day_index: int
    date_value: date | None = None
    title: str | None = None
    activities: list[ItineraryActivityResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class GenerateItineraryRequest(BaseModel):
    force_regenerate: bool = False


class AdjustItineraryRequest(BaseModel):
    instruction: str = Field(..., min_length=1)


class ItineraryResponse(BaseModel):
    workspace_id: int
    days: list[ItineraryDayResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
