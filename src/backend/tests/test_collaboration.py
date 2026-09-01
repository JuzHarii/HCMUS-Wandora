from fastapi.testclient import TestClient


def test_collaboration_flow(client: TestClient) -> None:
    """Kiểm tra mời thành viên, xem danh sách, cập nhật vai trò và xóa thành viên."""
    # 1. Tạo workspace
    ws_res = client.post("/api/v1/workspaces", json={"title": "Team Trip 2026"})
    assert ws_res.status_code == 201
    ws_id = ws_res.json()["id"]

    # 2. Mời thành viên mới
    invite_res = client.post(
        f"/api/v1/workspaces/{ws_id}/members",
        json={"email": "alice@example.com", "role": "editor"},
    )
    assert invite_res.status_code == 201
    inv_data = invite_res.json()
    assert inv_data["user_email"] == "alice@example.com"
    assert inv_data["role"] == "editor"
    user_id = inv_data["user_id"]

    # 3. Lấy danh sách thành viên
    list_res = client.get(f"/api/v1/workspaces/{ws_id}/members")
    assert list_res.status_code == 200
    members = list_res.json()
    # Chủ sở hữu (test user) + thành viên được mời = 2
    assert len(members) == 2
    alice_member = next((m for m in members if m["user_email"] == "alice@example.com"), None)
    assert alice_member is not None

    # 4. Cập nhật vai trò (phân quyền) sang viewer
    update_res = client.put(
        f"/api/v1/workspaces/{ws_id}/members/{user_id}",
        json={"role": "viewer"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["role"] == "viewer"

    # 5. Xóa thành viên
    del_res = client.delete(f"/api/v1/workspaces/{ws_id}/members/{user_id}")
    assert del_res.status_code == 200

    # Verification: Chỉ còn lại chủ sở hữu
    list_res2 = client.get(f"/api/v1/workspaces/{ws_id}/members")
    assert len(list_res2.json()) == 1
