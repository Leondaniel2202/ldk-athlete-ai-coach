"""API endpoint tests for root and health routes."""

from fastapi.testclient import TestClient

from ldk_athlete_ai_coach.main import app

client = TestClient(app)


def test_root_endpoint_returns_backend_message() -> None:
    """Validate the root endpoint returns the expected backend message."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "ldk-athlete-ai-coach backend"}


def test_health_endpoint_returns_ok_status() -> None:
    """Validate the health endpoint returns an ok status payload."""
    response = client.get("/api/v1/system/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
