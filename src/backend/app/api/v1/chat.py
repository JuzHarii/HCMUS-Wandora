from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chat import ChatMessage
from app.schemas.chat import ChatHistoryResponse, ChatMessageCreate, ChatMessageResponse

router = APIRouter()


@router.post(
    "/workspaces/{workspace_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_chat_message(
    workspace_id: Any, payload: ChatMessageCreate, db: Session = Depends(get_db)
) -> ChatMessageResponse:
    ws_id_val = int(workspace_id) if str(workspace_id).isdigit() else workspace_id
    message = ChatMessage(workspace_id=ws_id_val, role="user", sender_role="user", content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return ChatMessageResponse.model_validate(message)


@router.get("/workspaces/{workspace_id}/messages", response_model=ChatHistoryResponse)
def get_chat_messages(workspace_id: Any, db: Session = Depends(get_db)) -> ChatHistoryResponse:
    ws_id_val = int(workspace_id) if str(workspace_id).isdigit() else workspace_id
    messages = db.query(ChatMessage).filter(ChatMessage.workspace_id == ws_id_val).all()
    return ChatHistoryResponse(
        workspace_id=ws_id_val,
        messages=[ChatMessageResponse.model_validate(m) for m in messages],
    )
