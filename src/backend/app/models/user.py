from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """Người dùng trong hệ thống."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    workspace_memberships: Mapped[list["WorkspaceMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    memberships: Mapped[list["WorkspaceMember"]] = relationship(back_populates="user", cascade="all, delete-orphan", viewonly=True)


class WorkspaceMember(Base):
    """Liên kết người dùng với workspace và vai trò RBAC."""

    __tablename__ = "workspace_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    is_owner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship(back_populates="workspace_memberships")
