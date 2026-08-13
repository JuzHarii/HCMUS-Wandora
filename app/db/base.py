"""Base model cho toàn bộ entity của CSDL."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Lớp cơ sở cho ORM SQLAlchemy."""
