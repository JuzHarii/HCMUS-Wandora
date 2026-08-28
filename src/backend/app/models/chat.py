from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChatMessage(Base):
    """Một tin nhắn trong không gian hội thoại của workspace."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    sender_role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    workspace: Mapped["Workspace"] = relationship(back_populates="chat_messages")
