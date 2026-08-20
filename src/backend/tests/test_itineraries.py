from fastapi.testclient import TestClient


def test_itinerary_lifecycle_and_hardening(client: TestClient) -> None:
    """Kiểm tra toàn bộ luồng itinerary + cờ force_regenerate + is_manual = True."""
    # 1. Tạo workspace
    ws_res = client.post(
        "/api/v1/workspaces",
        json={
            "title": "Du lịch Đà Lạt",
            "destination": "Đà Lạt",
            "start_date": "2026-10-10",
            "end_date": "2026-10-12",
        },
    )
    assert ws_res.status_code == 201
    ws_id = ws_res.json()["id"]

    # 2. Sinh lịch trình ban đầu (force_regenerate=False)
    gen_res = client.post(f"/api/v1/workspaces/{ws_id}/generate-itinerary", json={"force_regenerate": False})
    assert gen_res.status_code == 200
    itin_data = gen_res.json()
    assert itin_data["workspace_id"] == ws_id
    assert len(itin_data["days"]) == 3
    day1_id = itin_data["days"][0]["id"]
    initial_activities_count = len(itin_data["days"][0]["activities"])
    assert initial_activities_count > 0

    # 3. Gọi lại generate-itinerary với force_regenerate=False -> Trả về lịch trình cũ không sinh lại
    gen_res2 = client.post(f"/api/v1/workspaces/{ws_id}/generate-itinerary", json={"force_regenerate": False})
    assert gen_res2.status_code == 200
    assert gen_res2.json() == itin_data

    # 4. Thêm thủ công 1 activity (Cưỡng chế is_manual=True)
    add_act_res = client.post(
        "/api/v1/itineraries/activities",
        json={
            "day_id": day1_id,
            "title": "Gặp bạn cũ tại quán cafe Đà Lạt",
            "start_time": "15:00",
            "end_time": "16:30",
            "location_name": "Túi Mơ To",
            "notes": "Hẹn nhóm bạn cấp 3",
        },
    )
    assert add_act_res.status_code == 201
    manual_act = add_act_res.json()
    assert manual_act["is_manual"] is True
    assert manual_act["title"] == "Gặp bạn cũ tại quán cafe Đà Lạt"
    manual_act_id = manual_act["id"]

    # 5. Cập nhật thông tin activity vừa thêm
    update_act_res = client.put(
        f"/api/v1/itineraries/activities/{manual_act_id}",
        json={"title": "Gặp bạn thân tại quán cafe Túi Mơ To", "notes": "Cập nhật giờ hẹn"},
    )
    assert update_act_res.status_code == 200
    assert update_act_res.json()["title"] == "Gặp bạn thân tại quán cafe Túi Mơ To"

    # 6. Gọi generate-itinerary với force_regenerate=True -> AI activities sinh lại, manual activity được giữ nguyên!
    regen_res = client.post(f"/api/v1/workspaces/{ws_id}/generate-itinerary", json={"force_regenerate": True})
    assert regen_res.status_code == 200
    new_itin_data = regen_res.json()
    day1_activities = new_itin_data["days"][0]["activities"]

    # Kiểm tra activity thủ công vẫn còn xuất hiện trong day 1
    manual_found = any(a["id"] == manual_act_id and a["is_manual"] is True for a in day1_activities)
    assert manual_found is True

    # 7. Điều chỉnh lịch trình theo yêu cầu mới (adjust-itinerary)
    adjust_res = client.post(
        f"/api/v1/workspaces/{ws_id}/adjust-itinerary",
        json={"instruction": "Thêm hoạt động ngắm bình minh vào buổi sáng ngày 2"},
    )
    assert adjust_res.status_code == 200
    assert adjust_res.json()["workspace_id"] == ws_id
