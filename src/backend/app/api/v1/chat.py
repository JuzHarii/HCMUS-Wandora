from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatHistoryResponse, ChatMessageCreate, ChatMessageResponse
from app.models.chat import ChatMessage

router = APIRouter()


@router.post(
    "/workspaces/{workspace_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_chat_message(
    workspace_id: str,
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatMessageResponse:
    message = ChatMessage(workspace_id=str(workspace_id), role="user", sender_role="user", content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return ChatMessageResponse.model_validate(message)


@router.get("/workspaces/{workspace_id}/messages", response_model=ChatHistoryResponse)
def get_chat_messages(
    workspace_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatHistoryResponse:
    messages = db.query(ChatMessage).filter(ChatMessage.workspace_id == str(workspace_id)).all()
    return ChatHistoryResponse(
        workspace_id=workspace_id,
        messages=[ChatMessageResponse.model_validate(m) for m in messages],
    )
