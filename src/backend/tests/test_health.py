from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    """Kiểm tra endpoint /health trả về status 200 ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
