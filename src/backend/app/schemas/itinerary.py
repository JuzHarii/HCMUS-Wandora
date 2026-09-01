from datetime import date, datetime, time
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_serializer, field_validator


def parse_time_safe(v: Any) -> time | None:
    if isinstance(v, time):
        return v
    if isinstance(v, str):
        try:
            parts = v.strip().split(":")
            if len(parts) >= 2:
                return time(hour=int(parts[0]), minute=int(parts[1]))
        except Exception:
            return None
    return None


def format_time_safe(v: time | str | None) -> str | None:
    if isinstance(v, time):
        return v.strftime("%H:%M")
    return v


class ItineraryActivityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    start_time: time | str | None = None
    end_time: time | str | None = None
    location_name: str | None = None
    activity_type: str | None = None
    notes: str | None = None
    external_url: str | None = None
    is_manual: bool = False
    order_index: int = 0
    sort_order: int = 0

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time(cls, v: Any) -> time | None:
        return parse_time_safe(v)


class ItineraryActivityCreate(ItineraryActivityBase):
    day_id: int | str | None = None
    workspace_id: int | str | None = None
    day_index: int | None = None
    is_manual: bool = True


class ActivityBase(ItineraryActivityBase):
    pass


class ActivityCreate(ItineraryActivityCreate):
    pass


class ActivityUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    start_time: time | str | None = None
    end_time: time | str | None = None
    location_name: str | None = None
    activity_type: str | None = None
    notes: str | None = None
    external_url: str | None = None
    order_index: int | None = None
    sort_order: int | None = None

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_time(cls, v: Any) -> time | None:
        return parse_time_safe(v)


class ItineraryActivityUpdate(ActivityUpdate):
    pass


class ItineraryActivityResponse(BaseModel):
    id: int | str
    day_id: int | str
    title: str
    start_time: time | str | None = None
    end_time: time | str | None = None
    location_name: str | None = None
    activity_type: str | None = None
    notes: str | None = None
    external_url: str | None = None
    is_manual: bool = False
    order_index: int = 0
    sort_order: int = 0

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("start_time", "end_time")
    def serialize_time(self, v: time | str | None) -> str | None:
        return format_time_safe(v)


class ActivityResponse(ItineraryActivityResponse):
    pass


class ItineraryDayResponse(BaseModel):
    id: int | str
    workspace_id: int | str | None = None
    day_index: int
    date_value: date | None = None
    travel_date: date | None = None
    title: str | None = None
    summary: str | None = None
    activities: list[ItineraryActivityResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ItineraryResponse(BaseModel):
    workspace_id: int | str
    generation_source: str | None = None
    generated_at: datetime | None = None
    days: list[ItineraryDayResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ItineraryVersionResponse(BaseModel):
    id: int | str
    generation_source: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GenerateItineraryRequest(BaseModel):
    force_regenerate: bool = False


class AdjustItineraryRequest(BaseModel):
    instruction: str = Field(min_length=1, validation_alias=AliasChoices("instruction", "prompt"))


class GeneratedActivityPayload(BaseModel):
    start_time: str | None = None
    end_time: str | None = None
    title: str
    location_name: str | None = None
    activity_type: str | None = None
    notes: str | None = None
    external_url: str | None = None


class GeneratedDayPayload(BaseModel):
    day_index: int
    title: str
    summary: str | None = None
    travel_date: str | None = None
    activities: list[GeneratedActivityPayload] = Field(default_factory=list)


class GeneratedItineraryPayload(BaseModel):
    days: list[GeneratedDayPayload] = Field(default_factory=list)


class ItineraryPreviewRequest(BaseModel):
    destination: str
    start_date: date | None = None
    end_date: date | None = None
    budget: int | None = None
    travel_style: str | None = None
    group_size: int | None = None
    notes: str | None = None


class ItineraryPreviewResponse(BaseModel):
    source: str
    draft: GeneratedItineraryPayload


class SaveItineraryDraftRequest(BaseModel):
    source: str
    draft: GeneratedItineraryPayload
