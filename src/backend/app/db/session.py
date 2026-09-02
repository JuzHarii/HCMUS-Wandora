"""Khởi tạo engine, session và tự động tạo bảng."""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

engine_options: dict[str, object] = {
    "future": True,
    "echo": settings.debug,
    "pool_pre_ping": True,
}

if settings.database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
elif settings.db_pool_mode == "transaction":
    engine_options.update(
        poolclass=NullPool,
        connect_args={"prepare_threshold": None},
    )
else:
    engine_options.update(
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )

engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

if settings.database_url.startswith("sqlite"):

    @event.listens_for(Engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
        """Bật ràng buộc khóa ngoại cho SQLite ngay khi mở kết nối."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """Dependency cung cấp session CSDL cho API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
