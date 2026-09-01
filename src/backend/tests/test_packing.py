from fastapi.testclient import TestClient


def test_packing_and_luggage_planning(client: TestClient) -> None:
    """Kiểm tra sinh hành lý gợi ý, thêm đồ dùng thủ công, phân công thành viên và hoàn thành."""
    # 1. Tạo workspace
    ws_res = client.post("/api/v1/workspaces", json={"title": "Packing Test Trip", "destination": "Nha Trang"})
    assert ws_res.status_code == 201
    ws_id = ws_res.json()["id"]

    # 2. Sinh gợi ý hành lý AI
    sug_res = client.post(f"/api/v1/workspaces/{ws_id}/packing/suggestions")
    assert sug_res.status_code == 200
    items = sug_res.json()
    assert len(items) > 0

    # 3. Thêm đồ dùng thủ công
    add_res = client.post(
        f"/api/v1/workspaces/{ws_id}/packing",
        json={"name": "Kính mát du lịch", "quantity": 1, "is_shared": True, "note": "Kính râm chống tia UV"},
    )
    assert add_res.status_code == 201
    custom_item = add_res.json()
    item_id = custom_item["id"]
    assert custom_item["name"] == "Kính mát du lịch"

    # 4. Phân công vật dụng cho user và tích cờ hoàn thành
    assign_res = client.post(
        f"/api/v1/packing/items/{item_id}/assign",
        json={"user_id": 1, "is_checked": True},
    )
    assert assign_res.status_code == 200
    ass_data = assign_res.json()
    assert len(ass_data["assignments"]) == 1
    assert ass_data["assignments"][0]["is_checked"] is True

    # 5. Xóa đồ dùng hành lý
    del_res = client.delete(f"/api/v1/packing/items/{item_id}")
    assert del_res.status_code == 200
