from fastapi.testclient import TestClient

from app.main import app


def test_health_contract():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_empty_message_rejected():
    with TestClient(app) as client:
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code == 422
