from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CheckDuplicateRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date


class TripResponse(BaseModel):
    id: str | int
    owner_id: str | int | None = None
    title: str
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "Draft"
    history_snapshots: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckDuplicateResponse(BaseModel):
    has_duplicate: bool
    duplicate_destination: bool
    overlapping_dates: bool
    warnings: list[str]
    matching_trips: list[TripResponse]


class SaveItineraryRequest(BaseModel):
    workspace_id: str | int | None = None
    trip_id: str | int | None = None  # Alias cho workspace_id
    title: str
    destination: str
    start_date: date
    end_date: date
    itinerary_data: dict[str, Any]


class VersionSummary(BaseModel):
    version: int
    created_at: str
    item_count: int | None = None


class RestoreVersionResponse(BaseModel):
    message: str
    workspace_id: str | int
    restored_version: int
    current_status: str
    itinerary_data: dict[str, Any]
