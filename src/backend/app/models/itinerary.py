from datetime import date, datetime, time

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ItineraryDay(Base):
    """Một ngày trong lịch trình."""

    __tablename__ = "itinerary_days"
    __table_args__ = (UniqueConstraint("workspace_id", "day_index", name="uq_itinerary_days_workspace_day_index"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    day_index: Mapped[int] = mapped_column(Integer, nullable=False)
    date_value: Mapped[date | None] = mapped_column("date", Date, nullable=True)
    travel_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    workspace: Mapped["Workspace"] = relationship(back_populates="itinerary_days")
    activities: Mapped[list["ItineraryActivity"]] = relationship(back_populates="day", cascade="all, delete-orphan", order_by="ItineraryActivity.order_index")


class ItineraryActivity(Base):
    """Thẻ hoạt động chi tiết trong từng ngày."""

    __tablename__ = "itinerary_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day_id: Mapped[int] = mapped_column(ForeignKey("itinerary_days.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_manual: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    day: Mapped[ItineraryDay] = relationship(back_populates="activities")


class ItineraryVersion(Base):
    """Snapshot khôi phục được, lưu trước mỗi lần AI thay itinerary."""

    __tablename__ = "itinerary_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    generation_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    snapshot: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
