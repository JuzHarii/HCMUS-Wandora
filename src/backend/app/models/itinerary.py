from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"
    __table_args__ = (UniqueConstraint("workspace_id", "day_index", name="uq_itinerary_days_workspace_day_index"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    day_index: Mapped[int] = mapped_column(Integer, nullable=False)
    date_value: Mapped[date | None] = mapped_column("date", Date, nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    activities: Mapped[list["ItineraryActivity"]] = relationship(back_populates="day", cascade="all, delete-orphan")


class ItineraryActivity(Base):
    __tablename__ = "itinerary_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_id: Mapped[int] = mapped_column(ForeignKey("itinerary_days.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_manual: Mapped[bool] = mapped_column(default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    day: Mapped[ItineraryDay] = relationship(back_populates="activities")
