from fastapi.testclient import TestClient

from ldk_athlete_ai_coach.main import app


client = TestClient(app)


def test_root_endpoint_returns_backend_message() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "ldk-athlete-ai-coach backend"}


def test_health_endpoint_returns_ok_status() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
