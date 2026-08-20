from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class MemberInviteRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    role: str = Field(default="member", description="Vai trò: owner, editor, viewer, member")


class MemberRoleUpdateRequest(BaseModel):
    role: str = Field(..., description="Vai trò mới: owner, editor, viewer, member")


class WorkspaceMemberResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    user_email: str | None = None
    user_full_name: str | None = None
    role: str
    joined_at: datetime

    model_config = {"from_attributes": True}
