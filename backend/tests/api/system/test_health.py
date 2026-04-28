"""API endpoint tests for root and health routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.api


def test_root_endpoint_returns_backend_message(app_client: TestClient) -> None:
    """Validate the root endpoint returns the expected backend message."""
    response = app_client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "ldk-athlete-ai-coach backend"}


def test_health_endpoint_returns_ok_status(app_client: TestClient) -> None:
    """Validate the health endpoint returns an ok status payload."""
    response = app_client.get("/api/v1/system/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_allows_frontend_origin(app_client: TestClient) -> None:
    """Validate local frontend origin receives CORS response headers."""
    response = app_client.get(
        "/api/v1/system/health",
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
