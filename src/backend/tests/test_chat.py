from fastapi.testclient import TestClient


def test_chat_flow(client: TestClient) -> None:
    """Kiểm tra gửi tin nhắn và đọc lịch sử nhắn tin."""
    # Tạo workspace
    ws_res = client.post("/api/v1/workspaces", json={"title": "Test Chat Trip"})
    assert ws_res.status_code == 201
    ws_id = ws_res.json()["id"]

    # Gửi tin nhắn
    msg_res = client.post(
        f"/api/v1/chat/workspaces/{ws_id}/messages",
        json={"content": "Tôi muốn đi ăn hải sản ở đâu ngon?"},
    )
    assert msg_res.status_code == 201
    msg_data = msg_res.json()
    assert msg_data["workspace_id"] == ws_id
    assert msg_data["content"] == "Tôi muốn đi ăn hải sản ở đâu ngon?"
    assert msg_data["sender_role"] == "user"

    # Đọc lịch sử
    hist_res = client.get(f"/api/v1/chat/workspaces/{ws_id}/messages")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["workspace_id"] == ws_id
    assert len(hist_data["messages"]) == 1
    assert hist_data["messages"][0]["content"] == "Tôi muốn đi ăn hải sản ở đâu ngon?"
