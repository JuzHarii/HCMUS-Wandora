import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.time_utils import parse_time_safe
from app.models.itinerary import ItineraryActivity, ItineraryDay
from app.models.workspace import Workspace


def test_sqlite_foreign_keys_cascade(db_session: Session) -> None:
    """Kiểm tra SQLite Foreign Key ON và Cascade Delete."""
    ws = Workspace(title="FK Test Workspace")
    db_session.add(ws)
    db_session.commit()
    db_session.refresh(ws)

    day = ItineraryDay(workspace_id=ws.id, day_index=1, title="Day 1")
    db_session.add(day)
    db_session.commit()
    db_session.refresh(day)

    act = ItineraryActivity(day_id=day.id, title="Test Activity", is_manual=True)
    db_session.add(act)
    db_session.commit()
    db_session.refresh(act)

    day_id = day.id
    act_id = act.id

    # Xóa workspace -> cascade xóa day và activity
    db_session.delete(ws)
    db_session.commit()

    assert db_session.query(ItineraryDay).filter(ItineraryDay.id == day_id).first() is None
    assert db_session.query(ItineraryActivity).filter(ItineraryActivity.id == act_id).first() is None


def test_unique_constraint_workspace_day_index(db_session: Session) -> None:
    """Kiểm tra Ràng buộc duy nhất (workspace_id, day_index)."""
    ws = Workspace(title="Unique Constraint Workspace")
    db_session.add(ws)
    db_session.commit()

    day1 = ItineraryDay(workspace_id=ws.id, day_index=1, title="Day 1 First")
    db_session.add(day1)
    db_session.commit()

    # Cố tình thêm ngày thứ 2 trùng workspace_id và day_index=1
    day1_dup = ItineraryDay(workspace_id=ws.id, day_index=1, title="Day 1 Duplicate")
    db_session.add(day1_dup)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_parse_time_safe_utils() -> None:
    """Kiểm tra bộ parser thời gian an toàn."""
    parsed = parse_time_safe("08:30")
    assert parsed is not None
    assert parsed.hour == 8
    assert parsed.minute == 30

    parsed_sec = parse_time_safe("14:45:10")
    assert parsed_sec is not None
    assert parsed_sec.second == 10
    assert parse_time_safe("invalid-time") is None
    assert parse_time_safe(None) is None
