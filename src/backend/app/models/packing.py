from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class PackingItem(Base):
    __tablename__ = "packing_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PackingListEntry(Base):
    __tablename__ = "packing_list_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    packing_item_id: Mapped[int] = mapped_column(ForeignKey("packing_items.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
