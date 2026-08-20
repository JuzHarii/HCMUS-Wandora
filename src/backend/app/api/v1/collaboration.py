from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...schemas.collaboration import MemberInviteRequest, MemberRoleUpdateRequest, WorkspaceMemberResponse
from ...services import collaboration_service

router = APIRouter()


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_workspace_member(
    workspace_id: int, payload: MemberInviteRequest, db: Session = Depends(get_db)
) -> WorkspaceMemberResponse:
    """Mời thành viên mới vào workspace."""
    res = collaboration_service.invite_member(db, workspace_id, email=payload.email, role=payload.role)
    return WorkspaceMemberResponse.model_validate(res)


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberResponse])
async def list_workspace_members(workspace_id: int, db: Session = Depends(get_db)) -> list[WorkspaceMemberResponse]:
    """Lấy danh sách tất cả các thành viên trong workspace."""
    res = collaboration_service.list_members(db, workspace_id)
    return [WorkspaceMemberResponse.model_validate(m) for m in res]


@router.put("/{workspace_id}/members/{user_id}", response_model=WorkspaceMemberResponse)
async def update_member_role(
    workspace_id: int, user_id: int, payload: MemberRoleUpdateRequest, db: Session = Depends(get_db)
) -> WorkspaceMemberResponse:
    """Cập nhật vai trò (phân quyền) của thành viên trong workspace."""
    res = collaboration_service.update_member_role(db, workspace_id, user_id=user_id, new_role=payload.role)
    return WorkspaceMemberResponse.model_validate(res)


@router.delete("/{workspace_id}/members/{user_id}")
async def remove_member(workspace_id: int, user_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    """Xóa thành viên khỏi workspace."""
    return collaboration_service.remove_member(db, workspace_id, user_id=user_id)
