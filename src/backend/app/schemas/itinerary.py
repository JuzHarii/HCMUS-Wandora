"""Schemas cho lịch trình và điều chỉnh AI."""

from datetime import date, datetime, time

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.schemas.workspace import WorkspaceBase


class ActivityBase(BaseModel):
    """Dữ liệu chung của một hoạt động."""

    start_time: time | None = None
    end_time: time | None = None
    title: str = Field(min_length=1)
    location_name: str | None = None
    activity_type: str | None = None
    notes: str | None = None
    external_url: str | None = None
    is_manual: bool = False
    sort_order: int = 0


class ActivityCreate(ActivityBase):
    """Payload thêm hoạt động thủ công."""

    day_id: str


class ActivityUpdate(BaseModel):
    """Payload cập nhật hoạt động."""

    start_time: time | None = None
    end_time: time | None = None
    title: str | None = None
    location_name: str | None = None
    activity_type: str | None = None
    notes: str | None = None
    external_url: str | None = None
    sort_order: int | None = None


class ActivityResponse(ActivityBase):
    """Hoạt động trả về cho UI."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    day_id: str
    created_at: datetime
    updated_at: datetime


class ItineraryDayResponse(BaseModel):
    """Một ngày lịch trình kèm các hoạt động."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    day_index: int
    travel_date: date | None = None
    title: str
    summary: str | None = None
    activities: list[ActivityResponse]


class ItineraryResponse(BaseModel):
    """Phản hồi xem lịch trình dạng timeline/map."""

    workspace_id: str
    generation_source: str | None = None
    generated_at: datetime | None = None
    days: list[ItineraryDayResponse]


class ItineraryVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    generation_source: str | None = None
    created_at: datetime


class GenerateItineraryRequest(BaseModel):
    """Yêu cầu sinh lịch trình bằng AI."""

    force_regenerate: bool = False


class AdjustItineraryRequest(BaseModel):
    """Yêu cầu điều chỉnh lịch trình bằng tiếng Việt tự nhiên."""

    instruction: str = Field(min_length=1, validation_alias=AliasChoices("instruction", "prompt"))


class GeneratedActivityPayload(BaseModel):
    """Hoạt động do AI sinh ra."""

    start_time: str | None = None
    end_time: str | None = None
    title: str
    location_name: str | None = None
    activity_type: str | None = None
    notes: str | None = None
    external_url: str | None = None


class GeneratedDayPayload(BaseModel):
    """Một ngày do AI sinh ra."""

    day_index: int
    title: str
    summary: str | None = None
    travel_date: date | None = None
    activities: list[GeneratedActivityPayload]


class GeneratedItineraryPayload(BaseModel):
    """Toàn bộ lịch trình do AI sinh ra."""

    days: list[GeneratedDayPayload]


class ItineraryPreviewRequest(WorkspaceBase):
    """Preference payload used to create a temporary, unsaved AI draft."""


class ItineraryPreviewResponse(BaseModel):
    source: str
    draft: GeneratedItineraryPayload


class SaveItineraryDraftRequest(BaseModel):
    source: str
    draft: GeneratedItineraryPayload
