from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.user import User, WorkspaceMember
from .workspace_service import get_workspace


def invite_member(db: Session, workspace_id: Any, email: str, role: str = "member") -> dict[str, Any]:
    """
    Mời thành viên mới vào workspace thông qua Email.

    Công dụng:
    - Kiểm tra sự tồn tại của workspace.
    - Tìm kiếm người dùng theo email trong bảng `users`, nếu chưa có sẽ tự động khởi tạo người dùng mới.
    - Kiểm tra xem người dùng đã là thành viên của workspace chưa để tránh chèn trùng lặp.
    - Thêm bản ghi `WorkspaceMember` mới với vai trò quy định (`owner`, `editor`, `viewer`, `member`).
    """
    _ = get_workspace(db, workspace_id)

    email_clean = email.strip().lower()

    # Tìm hoặc tạo mới người dùng
    user = db.query(User).filter(User.email == email_clean).first()
    if not user:
        user = User(email=email_clean, full_name=email_clean.split("@")[0])
        db.add(user)
        db.flush()

    # Kiểm tra tư cách thành viên đã tồn tại
    existing_member = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == str(workspace_id), WorkspaceMember.user_id == user.id)
        .first()
    )
    if existing_member:
        raise HTTPException(status_code=400, detail="Người dùng đã là thành viên của workspace này")

    member = WorkspaceMember(workspace_id=str(workspace_id), user_id=user.id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)

    return {
        "id": member.id,
        "workspace_id": member.workspace_id,
        "user_id": user.id,
        "user_email": user.email,
        "user_full_name": user.full_name,
        "role": member.role,
        "joined_at": member.joined_at,
    }


def list_members(db: Session, workspace_id: Any) -> list[dict[str, Any]]:
    """
    Lấy danh sách tất cả các thành viên đang tham gia vào workspace kèm thông tin người dùng.
    """
    _ = get_workspace(db, workspace_id)

    members = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == str(workspace_id))
        .order_by(WorkspaceMember.joined_at.asc())
        .all()
    )

    result = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        result.append(
            {
                "id": m.id,
                "workspace_id": m.workspace_id,
                "user_id": m.user_id,
                "user_email": user.email if user else None,
                "user_full_name": user.full_name if user else None,
                "role": m.role,
                "joined_at": m.joined_at,
            }
        )
    return result


def update_member_role(db: Session, workspace_id: Any, user_id: Any, new_role: str) -> dict[str, Any]:
    """
    Cập nhật vai trò phân quyền của thành viên trong workspace (ví dụ chuyển từ viewer sang editor).
    """
    member = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == str(workspace_id), WorkspaceMember.user_id == str(user_id))
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên trong workspace")

    member.role = new_role
    db.commit()

    user = db.query(User).filter(User.id == str(user_id)).first()
    return {
        "id": member.id,
        "workspace_id": member.workspace_id,
        "user_id": user_id,
        "user_email": user.email if user else None,
        "user_full_name": user.full_name if user else None,
        "role": member.role,
        "joined_at": member.joined_at,
    }


def remove_member(db: Session, workspace_id: Any, user_id: Any) -> dict[str, str]:
    """
    Xóa thành viên khỏi workspace.
    """
    member = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == str(workspace_id), WorkspaceMember.user_id == str(user_id))
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên trong workspace")

    db.delete(member)
    db.commit()
    return {"detail": "Đã xóa thành viên khỏi workspace thành công"}
