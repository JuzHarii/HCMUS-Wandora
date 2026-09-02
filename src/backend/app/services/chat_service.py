from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.chat import ChatMessage
from .workspace_service import get_workspace


def send_message(db: Session, workspace_id: int, content: str, sender_role: str = "user") -> ChatMessage:
    """Lưu tin nhắn chat mới vào workspace."""
    _ = get_workspace(db, workspace_id)  # Validate workspace exists

    msg = ChatMessage(
        workspace_id=workspace_id,
        sender_role=sender_role,
        content=content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_chat_history(db: Session, workspace_id: int, limit: int = 100) -> list[ChatMessage]:
    """Lịch sử tin nhắn chat của workspace."""
    _ = get_workspace(db, workspace_id)

    return (
        db.query(ChatMessage)
        .filter(ChatMessage.workspace_id == workspace_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
