from fastapi.testclient import TestClient


def test_create_and_get_workspace(client: TestClient) -> None:
    """Kiểm tra tạo mới và lấy thông tin workspace."""
    payload = {
        "title": "Chuyến đi Đà Nẵng 2026",
        "destination": "Đà Nẵng",
        "start_date": "2026-09-01",
        "end_date": "2026-09-03",
        "preferences": {"budget": "medium", "pace": "relaxed"},
    }

    create_res = client.post("/api/v1/workspaces", json=payload)
    assert create_res.status_code == 201
    ws_data = create_res.json()
    assert ws_data["title"] == payload["title"]
    assert ws_data["destination"] == payload["destination"]
    assert ws_data["preferences"] == payload["preferences"]
    ws_id = ws_data["id"]

    # Lấy thông tin chi tiết
    get_res = client.get(f"/api/v1/workspaces/{ws_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == payload["title"]

    # Lấy danh sách workspace
    list_res = client.get("/api/v1/workspaces")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Lấy overview
    overview_res = client.get(f"/api/v1/workspaces/{ws_id}/overview")
    assert overview_res.status_code == 200
    ov_data = overview_res.json()
    assert ov_data["workspace_id"] == ws_id
    assert ov_data["total_days"] == 3
