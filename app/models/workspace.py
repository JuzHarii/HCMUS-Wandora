"""Các entity cốt lõi của workspace và dữ liệu chuyến đi."""

from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Workspace(Base):
    """Workspace đại diện cho một chuyến đi."""

    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    travel_style: Mapped[str | None] = mapped_column(String(255), nullable=True)
    group_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    destinations: Mapped[list["WorkspaceDestination"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    itinerary_days: Mapped[list["ItineraryDay"]] = relationship(back_populates="workspace", cascade="all, delete-orphan", order_by="ItineraryDay.day_index")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")


class Location(Base):
    """Địa điểm tham chiếu trong hệ thống."""

    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    google_maps_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class WorkspaceDestination(Base):
    """Danh sách điểm đến của workspace theo thứ tự ưu tiên."""

    __tablename__ = "workspace_destinations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id"), nullable=False)
    location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"), nullable=True)
    destination_name: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    workspace: Mapped[Workspace] = relationship(back_populates="destinations")
    location: Mapped[Location | None] = relationship()


class InviteToken(Base):
    """Mã mời tham gia workspace."""

    __tablename__ = "invite_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
