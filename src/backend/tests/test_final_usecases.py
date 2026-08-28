from datetime import date

from fastapi.testclient import TestClient

from app.models.itinerary import ItineraryActivity, ItineraryDay
from app.models.user import User
from app.models.workspace import Workspace


def test_sprint1_auth_flow(client: TestClient) -> None:
    """Sprint 1: Test UC 2.12 Register & Login flow."""
    # 1. Register
    reg_payload = {
        "email": "testuser@wandora.com",
        "password": "SecretPassword123!",
        "full_name": "Test Traveler",
    }
    response = client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "testuser@wandora.com"
    assert "id" in user_data

    # 2. Duplicate registration attempt
    dup_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 400

    # 3. Login with wrong password
    bad_login = client.post("/api/v1/auth/login", json={"email": "testuser@wandora.com", "password": "WrongPassword"})
    assert bad_login.status_code == 401

    # 4. Login with correct password
    login_res = client.post("/api/v1/auth/login", json={"email": "testuser@wandora.com", "password": "SecretPassword123!"})
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_sprint2_and_3_trips_and_versions(client: TestClient, db_session) -> None:
    """Sprint 2 & 3: Test UC 2.16 (Check Duplicates), UC 2.13 (Save Itinerary + DB Persistence), UC 2.17 (History & Restore)."""
    # 1. Setup Auth User
    client.post("/api/v1/auth/register", json={"email": "tripper@wandora.com", "password": "Pass123!", "full_name": "Tripper"})
    login_res = client.post("/api/v1/auth/login", json={"email": "tripper@wandora.com", "password": "Pass123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. UC 2.16: Check duplicates (first time -> no duplicates)
    chk_payload = {
        "destination": "Da Nang",
        "start_date": "2026-09-01",
        "end_date": "2026-09-05",
    }
    dup_res = client.post("/api/v1/trips/check-duplicates", json=chk_payload, headers=headers)
    assert dup_res.status_code == 200
    dup_data = dup_res.json()
    assert dup_data["has_duplicate"] is False
    assert len(dup_data["matching_trips"]) == 0

    # 3. UC 2.13: Save AI Itinerary & Verify DB Persistence
    save_payload = {
        "title": "Chuyến đi Đà Nẵng 5N4Đ",
        "destination": "Da Nang",
        "start_date": "2026-09-01",
        "end_date": "2026-09-05",
        "itinerary_data": {
            "destination": "Da Nang",
            "days": [
                {
                    "day_index": 1,
                    "title": "Ngày 1: Check in",
                    "activities": [
                        {"title": "Tắm biển Mỹ Khê", "location_name": "Mỹ Khê"},
                        {"title": "Ăn mì Quảng", "location_name": "Quán ếch"},
                    ],
                }
            ],
        },
    }
    save_res = client.post("/api/v1/trips/save-itinerary", json=save_payload, headers=headers)
    assert save_res.status_code == 201
    workspace_data = save_res.json()
    workspace_id = workspace_data["id"]
    assert workspace_data["status"] == "Planned"
    assert workspace_data["destination"] == "Da Nang"

    # Verify activities are REALLY written to DB tables itinerary_days and itinerary_activities!
    days_in_db = db_session.query(ItineraryDay).filter(ItineraryDay.workspace_id == workspace_id).all()
    assert len(days_in_db) == 1
    acts_in_db = db_session.query(ItineraryActivity).filter(ItineraryActivity.day_id == days_in_db[0].id).all()
    assert len(acts_in_db) == 2
    assert acts_in_db[0].title == "Tắm biển Mỹ Khê"

    # 4. UC 2.16: Check duplicates again (overlapping dates & same destination)
    overlap_res = client.post(
        "/api/v1/trips/check-duplicates",
        json={"destination": "Da Nang", "start_date": "2026-09-03", "end_date": "2026-09-07"},
        headers=headers,
    )
    assert overlap_res.status_code == 200
    overlap_data = overlap_res.json()
    assert overlap_data["has_duplicate"] is True
    assert overlap_data["duplicate_destination"] is True
    assert overlap_data["overlapping_dates"] is True
    assert len(overlap_data["warnings"]) >= 2

    # 5. UC 2.17: Get Trip History
    history_res = client.get("/api/v1/trips/history", headers=headers)
    assert history_res.status_code == 200
    history_list = history_res.json()
    assert len(history_list) >= 1
    assert history_list[0]["id"] == workspace_id

    # 6. UC 2.17: Get Versions list
    versions_res = client.get(f"/api/v1/trips/{workspace_id}/versions", headers=headers)
    assert versions_res.status_code == 200
    version_list = versions_res.json()
    assert len(version_list) == 1
    assert version_list[0]["version"] == 1

    # 7. UC 2.17: Restore version 1
    restore_res = client.post(f"/api/v1/trips/{workspace_id}/versions/1/restore", headers=headers)
    assert restore_res.status_code == 200
    restore_data = restore_res.json()
    assert restore_data["restored_version"] == 1
    assert "itinerary_data" in restore_data


def test_sprint4_guards_comments_and_voting(client: TestClient, db_session) -> None:
    """Sprint 4: Test UC 2.14 (check_trip_is_planned guard on real export API) & UC 2.15 (Comments & Voting)."""
    # 1. Setup Auth User
    client.post("/api/v1/auth/register", json={"email": "voter@wandora.com", "password": "Pass123!", "full_name": "Voter"})
    login_res = client.post("/api/v1/auth/login", json={"email": "voter@wandora.com", "password": "Pass123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    voter = db_session.query(User).filter(User.email == "voter@wandora.com").first()
    user_id = voter.id if voter else "test-user-id"

    # 2. UC 2.14: Test Draft Guard on REAL export API /api/v1/workspaces/{workspace_id}/export
    draft_ws = Workspace(
        owner_id=user_id,
        title="Draft Workspace to Hue",
        destination="Hue",
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 5),
        status="Draft",
    )
    db_session.add(draft_ws)
    db_session.commit()
    db_session.refresh(draft_ws)

    # Calling REAL export on Draft workspace should fail with 403 Forbidden
    forbidden_res = client.get(f"/api/v1/workspaces/{draft_ws.id}/export", headers=headers)
    assert forbidden_res.status_code == 403
    assert "Draft status" in forbidden_res.json()["detail"]

    # Change workspace status to Planned
    draft_ws.status = "Planned"
    db_session.commit()

    planned_res = client.get(f"/api/v1/workspaces/{draft_ws.id}/export", headers=headers)
    assert planned_res.status_code == 200
    assert "content" in planned_res.json()

    # 3. UC 2.15: Comments & Voting on Activity
    workspace = Workspace(title="Hue Trip Workspace", status="Planned")
    db_session.add(workspace)
    db_session.commit()

    day = ItineraryDay(workspace_id=workspace.id, day_index=1)
    db_session.add(day)
    db_session.commit()

    activity = ItineraryActivity(day_id=day.id, title="Thăm Đại Nội Huế", order_index=1)
    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)

    # Post Comment
    comment_payload = {"content": "Nên đi vào buổi sáng cho mát!"}
    cmt_res = client.post(f"/api/v1/activities/{activity.id}/comments", json=comment_payload, headers=headers)
    assert cmt_res.status_code == 201
    cmt_data = cmt_res.json()
    assert cmt_data["content"] == "Nên đi vào buổi sáng cho mát!"

    # Get Comments
    get_cmts_res = client.get(f"/api/v1/activities/{activity.id}/comments", headers=headers)
    assert get_cmts_res.status_code == 200
    cmt_list = get_cmts_res.json()
    assert len(cmt_list) == 1
    assert cmt_list[0]["content"] == "Nên đi vào buổi sáng cho mát!"

    # Vote Activity (Upvote = 1)
    vote_res = client.post(f"/api/v1/activities/{activity.id}/vote", json={"vote_value": 1}, headers=headers)
    assert vote_res.status_code == 200
    assert vote_res.json()["vote_value"] == 1

    # Vote Activity again (Upsert to Downvote = -1)
    revote_res = client.post(f"/api/v1/activities/{activity.id}/vote", json={"vote_value": -1}, headers=headers)
    assert revote_res.status_code == 200
    assert revote_res.json()["vote_value"] == -1
