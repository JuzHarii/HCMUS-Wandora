from fastapi.testclient import TestClient


def test_place_reviews(client: TestClient) -> None:
    """Kiểm tra tạo và danh sách đánh giá nhận xét địa điểm."""
    # 1. Tạo workspace
    ws_res = client.post("/api/v1/workspaces", json={"title": "Review Test Trip"})
    assert ws_res.status_code == 201
    ws_id = ws_res.json()["id"]

    # 2. Đánh giá địa điểm
    rev_res = client.post(
        f"/api/v1/workspaces/{ws_id}/reviews",
        json={
            "place_name": "Quán Phở Thìn Bờ Hồ",
            "rating": 5,
            "comment": "Phở rất ngon, nước dùng đậm đà!",
            "user_id": 1,
        },
    )
    assert rev_res.status_code == 201
    rev_data = rev_res.json()
    assert rev_data["rating"] == 5
    assert rev_data["place_name"] == "Quán Phở Thìn Bờ Hồ"

    # 3. Lấy danh sách đánh giá
    list_res = client.get(f"/api/v1/workspaces/{ws_id}/reviews")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
