from .base import Base
from .session import engine


def init_db() -> None:
    """Tạo các bảng DB nếu chưa tồn tại."""
    from .. import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
