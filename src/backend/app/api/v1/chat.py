from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.chat import ChatHistoryResponse, ChatMessageCreate, ChatMessageResponse
from ...services import chat_service

router = APIRouter()


@router.post(
    "/workspaces/{workspace_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_chat_message(
    workspace_id: int, payload: ChatMessageCreate, db: Session = Depends(get_db)
) -> ChatMessageResponse:
    """Gửi tin nhắn mới trong workspace."""
    msg = chat_service.send_message(db, workspace_id, content=payload.content, sender_role="user")
    return ChatMessageResponse.model_validate(msg)


@router.get("/workspaces/{workspace_id}/messages", response_model=ChatHistoryResponse)
async def get_chat_messages(workspace_id: int, db: Session = Depends(get_db)) -> ChatHistoryResponse:
    """Lấy lịch sử nhắn tin của workspace."""
    messages = chat_service.get_chat_history(db, workspace_id)
    return ChatHistoryResponse(
        workspace_id=workspace_id,
        messages=[ChatMessageResponse.model_validate(m) for m in messages],
    )
