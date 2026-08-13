"""API hội thoại và tương tác với trợ lý AI."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_workspace_member
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/workspaces/{workspace_id}/messages", response_model=ChatMessageResponse)
def send_message(
    workspace_id: str,
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatMessageResponse:
    """Ghi nhận một tin nhắn và trả lại phản hồi mô phỏng."""

    from app.models.chat import ChatMessage

    require_workspace_member(db, workspace_id, current_user.id)
    message = ChatMessage(workspace_id=workspace_id, role="user", content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
