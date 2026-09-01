from fastapi.testclient import TestClient


def test_share_and_export_flow(client: TestClient) -> None:
    """Kiểm tra sinh liên kết chia sẻ công khai, truy cập qua Token và xuất kế hoạch JSON/Markdown."""
    # 1. Tạo workspace và sinh lịch trình
    ws_res = client.post("/api/v1/workspaces", json={"title": "Share Test Trip", "destination": "Huế"})
    assert ws_res.status_code == 201
    ws_id = ws_res.json()["id"]

    client.post(f"/api/v1/workspaces/{ws_id}/generate-itinerary")

    # 2. Sinh liên kết chia sẻ
    share_res = client.post(f"/api/v1/workspaces/{ws_id}/share")
    assert share_res.status_code == 201
    share_data = share_res.json()
    token = share_data["token"]
    assert token is not None

    # 3. Truy cập công khai xem lịch trình qua Token
    public_res = client.get(f"/api/v1/share/{token}")
    assert public_res.status_code == 200
    assert public_res.json()["workspace_id"] == ws_id

    # 4. Xuất kế hoạch ra dạng Markdown
    md_res = client.get(f"/api/v1/workspaces/{ws_id}/export?format=markdown")
    assert md_res.status_code == 200
    md_data = md_res.json()
    assert md_data["format"] == "markdown"
    assert "# Kế hoạch chuyến đi: Share Test Trip" in md_data["content"]

    # 5. Xuất kế hoạch ra dạng JSON
    json_res = client.get(f"/api/v1/workspaces/{ws_id}/export?format=json")
    assert json_res.status_code == 200
    assert json_res.json()["format"] == "json"
