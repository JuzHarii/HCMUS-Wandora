"""Fast checks for PA4 UC01 validation and UC02's no-key fallback."""

import sys
from datetime import date
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "src" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.schemas.workspace import WorkspaceCreate
from app.services.ai_service import AIService


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
        {"destination": "Hoi An", "start_date": date(2026, 9, 1)},
    )
    assert len(draft.days) == 3
    assert all(day.activities for day in draft.days)
