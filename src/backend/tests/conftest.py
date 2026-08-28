from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.api.dependencies import get_current_user
from app.models.user import User

# Tạo CSDL SQLite trong bộ nhớ (in-memory) cho các bài kiểm thử
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
    """Kích hoạt ràng buộc khóa ngoại (PRAGMA foreign_keys=ON) cho kết nối SQLite thử nghiệm."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture(autouse=True)
def setup_db() -> Generator[None, None, None]:
    """Tự động khởi tạo và dọn dẹp cấu trúc bảng DB trước và sau mỗi bài kiểm thử."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Cung cấp Session kết nối DB cách biệt cho từng bài kiểm thử."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


def _make_test_user(db_session: Session) -> User:
    """Tạo và lưu một user test vào DB nếu chưa có."""
    user = db_session.query(User).filter(User.email == "test@wandora.app").first()
    if not user:
        user = User(email="test@wandora.app", full_name="Test User", hashed_password="hashed", role="member")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Khởi tạo FastAPI TestClient kết hợp ghi đè dependency get_db và get_current_user."""

    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    test_user = _make_test_user(db_session)

    def _override_get_current_user() -> User:
        return test_user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

