"""Khởi tạo engine, session và tự động tạo bảng."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

engine_options: dict[str, object] = {
    "future": True,
    "echo": settings.debug,
    "pool_pre_ping": True,
}

# Supavisor transaction mode is itself a connection pool and does not support
# prepared statements.  Let it manage connections instead of keeping another
# persistent pool in this FastAPI process.
if settings.db_pool_mode == "transaction":
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


def get_db() -> Generator[Session, None, None]:
    """Dependency cung cấp session CSDL cho API."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
