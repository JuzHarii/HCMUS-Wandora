from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ..core.config import get_settings

settings = get_settings()
engine_kwargs: dict[str, object] = {"future": True, "pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


if settings.database_url.startswith("sqlite"):

    @event.listens_for(Engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
        """Bật ràng buộc khóa ngoại cho SQLite ngay khi mở kết nối."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()



def get_db() -> Generator[Session, None, None]:
    """Cung cấp một session DB cho mỗi request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
