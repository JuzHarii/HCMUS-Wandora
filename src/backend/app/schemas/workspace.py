"""Schemas cho workspace và tổng quan chuyến đi."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkspaceBase(BaseModel):
    """Thông tin nền của một workspace."""

    title: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    start_date: date | None = None
    end_date: date | None = None
    budget: int | None = Field(default=None, ge=0)
    travel_style: str | None = None
    group_size: int | None = Field(default=None, ge=1)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_travel_dates(self) -> "WorkspaceBase":
        """Không cho phép ngày kết thúc đứng trước ngày khởi hành."""

        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("Ngày kết thúc phải sau hoặc bằng ngày bắt đầu.")
        return self


class WorkspaceCreate(WorkspaceBase):
    """Payload tạo workspace mới."""


class WorkspaceResponse(WorkspaceBase):
    """Phản hồi workspace chuẩn hóa."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    itinerary_source: str | None = None
    itinerary_generated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class WorkspaceDestinationPayload(BaseModel):
    """Schema cho từng điểm đến trong workspace."""

    destination_name: str
    order_index: int = 0


class TripOverviewResponse(BaseModel):
    """Tổng quan chuyến đi hiển thị cho UI 5A/5B."""

    workspace: WorkspaceResponse
    destinations: list[WorkspaceDestinationPayload]
    itinerary_days: int
    itinerary_activities: int
    manual_activities: int
