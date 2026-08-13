"""Smoke test the PA4 UC01 and UC02 API flows against the configured Supabase DB."""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "src" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from main import app


def run_smoke_test() -> None:
    """Create a trip, generate its itinerary, then verify it can be reloaded."""

    client = TestClient(app)
    suffix = uuid4().hex[:8]
    credentials = {
        "full_name": "PA4 Smoke User",
        "email": f"pa4-smoke-{suffix}@example.com",
        "password": "SecurePass!123",
    }
    signed_up = client.post("/api/v1/auth/signup", json=credentials)
    assert signed_up.status_code == 201, signed_up.text
    assert signed_up.json()["user"]["email"] == credentials["email"]
    duplicate_signup = client.post("/api/v1/auth/signup", json=credentials)
    assert duplicate_signup.status_code == 409, duplicate_signup.text

    invalid_login = client.post(
        "/api/v1/auth/login",
        json={"email": credentials["email"], "password": "WrongPass!123"},
    )
    assert invalid_login.status_code == 401, invalid_login.text

    logged_in = client.post(
        "/api/v1/auth/login",
        json={"email": credentials["email"], "password": credentials["password"]},
    )
    assert logged_in.status_code == 200, logged_in.text
    session = logged_in.json()
    auth_headers = {"Authorization": f"Bearer {session['access_token']}"}
    current_user = client.get("/api/v1/auth/me", headers=auth_headers)
    assert current_user.status_code == 200, current_user.text
    assert current_user.json()["email"] == credentials["email"]
    workspace_payload = {
        "title": f"PA4 smoke trip {suffix}",
        "destination": "Da Nang",
        "start_date": "2026-09-01",
        "end_date": "2026-09-03",
        "budget": 3000000,
        "travel_style": "Cultural",
        "group_size": 4,
        "notes": "Temporary automated smoke-test data.",
    }

    unauthenticated = client.post("/api/v1/workspaces", json=workspace_payload)
    assert unauthenticated.status_code == 401, unauthenticated.text

    created = client.post("/api/v1/workspaces", json=workspace_payload, headers=auth_headers)
    assert created.status_code == 201, created.text
    workspace = created.json()
    assert workspace["status"] == "Draft"
    workspace_id = workspace["id"]

    dashboard = client.get("/api/v1/workspaces", headers=auth_headers)
    assert dashboard.status_code == 200, dashboard.text
    assert any(item["id"] == workspace_id for item in dashboard.json())

    generated = client.post(
        f"/api/v1/workspaces/{workspace_id}/generate-itinerary",
        json={"force_regenerate": True},
        headers=auth_headers,
    )
    assert generated.status_code == 200, generated.text
    itinerary = generated.json()
    assert itinerary["workspace_id"] == workspace_id
    assert itinerary["days"] and all(day["activities"] for day in itinerary["days"])

    reloaded = client.get(f"/api/v1/workspaces/{workspace_id}/itinerary", headers=auth_headers)
    assert reloaded.status_code == 200, reloaded.text
    assert reloaded.json()["days"] == itinerary["days"]

    other_account = client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "PA4 Other User",
            "email": f"pa4-other-{suffix}@example.com",
            "password": "SecurePass!123",
        },
    )
    assert other_account.status_code == 201, other_account.text
    other_headers = {"Authorization": f"Bearer {other_account.json()['access_token']}"}
    forbidden_workspace = client.get(f"/api/v1/workspaces/{workspace_id}/overview", headers=other_headers)
    assert forbidden_workspace.status_code == 403, forbidden_workspace.text

    invalid_dates = client.post(
        "/api/v1/workspaces",
        json={**workspace_payload, "title": f"Invalid {suffix}", "start_date": "2026-09-03", "end_date": "2026-09-01"},
        headers=auth_headers,
    )
    assert invalid_dates.status_code == 422, invalid_dates.text
    print(f"PASS auth + UC01 + UC02: workspace {workspace_id} created, protected, generated, and reloaded.")


if __name__ == "__main__":
    run_smoke_test()
