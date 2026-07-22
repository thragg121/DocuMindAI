from fastapi.testclient import TestClient


def test_health_check_returns_success(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["service"] == "DocuMindAI"
    assert isinstance(body["timestamp"], str)
    assert body["timestamp"]
