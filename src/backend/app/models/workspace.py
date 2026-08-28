import json
from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Workspace(Base):
    """Workspace đại diện cho một chuyến đi."""

    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Draft")
    itinerary_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    itinerary_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    travel_style: Mapped[str | None] = mapped_column(String(255), nullable=True)
    group_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferences_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    history_snapshots: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    owner: Mapped["User"] = relationship()
    destinations: Mapped[list["WorkspaceDestination"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    locations: Mapped[list["Location"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    invite_tokens: Mapped[list["InviteToken"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    itinerary_days: Mapped[list["ItineraryDay"]] = relationship(back_populates="workspace", cascade="all, delete-orphan", order_by="ItineraryDay.day_index")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")

    @property
    def preferences(self) -> dict[str, Any]:
        """Giải mã JSON preferences thành dict."""
        if self.preferences_json:
            try:
                return json.loads(self.preferences_json)  # type: ignore[no-any-return]
            except Exception:
                return {}
        return {}

    @property
    def snapshots(self) -> list[dict[str, Any]]:
        """Parse mảng JSON history_snapshots thành danh sách dict."""
        if self.history_snapshots:
            try:
                return json.loads(self.history_snapshots)  # type: ignore[no-any-return]
            except Exception:
                return []
        return []

    def set_snapshots(self, snapshots_list: list[dict[str, Any]]) -> None:
        """Lưu danh sách snapshots vào history_snapshots dưới dạng JSON string."""
        self.history_snapshots = json.dumps(snapshots_list, default=str)


class Location(Base):
    """Địa điểm tham chiếu trong hệ thống."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    google_maps_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace: Mapped[Workspace] = relationship(back_populates="locations")


class WorkspaceDestination(Base):
    """Danh sách điểm đến của workspace."""

    __tablename__ = "workspace_destinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    destination_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(255), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    workspace: Mapped[Workspace] = relationship(back_populates="destinations")
    location: Mapped[Location | None] = relationship()


class InviteToken(Base):
    """Mã mời tham gia workspace."""

    __tablename__ = "invite_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped[Workspace] = relationship(back_populates="invite_tokens")
