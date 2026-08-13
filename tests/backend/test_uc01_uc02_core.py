"""Fast checks for PA4 UC01 validation and UC02's no-key fallback."""

import sys
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "src" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.workspace import WorkspaceCreate
from app.models import ItineraryVersion, Workspace
from app.db.base import Base
from app.schemas.itinerary import ActivityCreate, GenerateItineraryRequest, GeneratedItineraryPayload
from app.services.ai_service import AIService, GenerationResult
from app.services.itinerary_service import ItineraryService


def test_uc01_accepts_a_valid_trip_payload():
    workspace = WorkspaceCreate(
        title="Trip to Da Nang",
        destination="Da Nang",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 3),
        group_size=3,
        budget=3000000,
    )
    assert workspace.destination == "Da Nang"


def test_uc01_rejects_an_end_date_before_start_date():
    with pytest.raises(ValueError, match="Ngày kết thúc"):
        WorkspaceCreate(
            title="Invalid trip",
            destination="Hue",
            start_date=date(2026, 9, 3),
            end_date=date(2026, 9, 1),
        )


def test_uc02_fallback_draft_has_days_and_activities(monkeypatch):
    service = AIService()
    monkeypatch.setattr(service.settings, "gemini_api_key", None)
    draft = service.generate_itinerary_draft(
        {
            "destination": "Hoi An",
            "start_date": date(2026, 9, 1),
            "end_date": date(2026, 9, 3),
        },
    )
    assert draft.source == "fallback"
    assert len(draft.draft.days) == 3
    assert [day.travel_date for day in draft.draft.days] == [date(2026, 9, 1), date(2026, 9, 2), date(2026, 9, 3)]
    assert all(day.activities for day in draft.draft.days)


def test_uc02_regenerate_preserves_manual_activity_and_can_restore_a_snapshot(monkeypatch):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    db = Session(engine)
    workspace = Workspace(
        title="Hoi An trip",
        destination="Hoi An",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 1),
    )
    db.add(workspace)
    db.commit()

    drafts = iter(("First plan", "Second plan"))

    def fake_generate(_: dict[str, object]) -> GenerationResult:
        title = next(drafts)
        return GenerationResult(
            draft=GeneratedItineraryPayload.model_validate(
                {
                    "days": [
                        {
                            "day_index": 1,
                            "title": title,
                            "travel_date": "2026-09-01",
                            "activities": [
                                {"title": f"AI activity from {title}", "start_time": "09:00", "end_time": "10:00"}
                            ],
                        }
                    ]
                }
            ),
            source="fallback",
        )

    service = ItineraryService(db)
    monkeypatch.setattr(service.ai_service, "generate_itinerary_draft", fake_generate)
    first_plan = service.generate_itinerary_draft(workspace.id)
    service.add_activity(ActivityCreate(day_id=first_plan.days[0].id, title="My booked cooking class"))
    second_plan = service.generate_itinerary_draft(workspace.id, request=GenerateItineraryRequest(force_regenerate=True))

    assert second_plan.days[0].title == "Second plan"
    assert {activity.title for activity in second_plan.days[0].activities} == {"AI activity from Second plan", "My booked cooking class"}
    assert db.scalar(select(func.count(ItineraryVersion.id))) == 1

    version = service.list_versions(workspace.id)[0]
    restored_plan = service.restore_version(workspace.id, version.id)
    assert restored_plan.days[0].title == "First plan"
    assert {activity.title for activity in restored_plan.days[0].activities} == {"AI activity from First plan", "My booked cooking class"}
