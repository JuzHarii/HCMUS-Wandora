from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PackingItem(Base):
    """Mục đồ dùng cần chuẩn bị cho chuyến đi."""

    __tablename__ = "packing_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PackingListEntry(Base):
    """Phân công hoặc trạng thái tích chọn đồ dùng."""

    __tablename__ = "packing_list_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    packing_item_id: Mapped[int] = mapped_column(ForeignKey("packing_items.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Rating(Base):
    """Đánh giá sau chuyến đi."""

    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
