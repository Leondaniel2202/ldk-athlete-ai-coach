"""API tests for the AI current-context analysis endpoint."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from ldk_athlete_ai_coach.ai.errors import AIConfigurationError, AIProviderError
from ldk_athlete_ai_coach.api.v1.schemas.ai import AnalyzeCurrentContextResponse
from ldk_athlete_ai_coach.main import app

client = TestClient(app)


def _analysis_response() -> AnalyzeCurrentContextResponse:
    return AnalyzeCurrentContextResponse(
        summary="Current training context looks coherent.",
        phase_focus="Build race-specific durability.",
        positives=["Workouts are aligned with the phase."],
        concerns=["Recent intensity may be clustered."],
        recommendation="Keep the current direction and protect recovery.",
    )


def test_ai_analysis_endpoint_returns_structured_response() -> None:
    """Endpoint returns a compact structured AI assessment on success."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.ai.build_analyze_current_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_current_context.return_value = _analysis_response()
        mock_builder.return_value = mock_service

        response = client.post("/api/v1/ai/analyze-current-context")

    assert response.status_code == 200
    assert response.json() == _analysis_response().model_dump(mode="json")
    mock_service.analyze_current_context.assert_called_once_with(None)


def test_ai_analysis_endpoint_accepts_empty_json_body() -> None:
    """Endpoint treats {} the same as an omitted request body."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.ai.build_analyze_current_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_current_context.return_value = _analysis_response()
        mock_builder.return_value = mock_service

        response = client.post("/api/v1/ai/analyze-current-context", json={})

    assert response.status_code == 200
    mock_service.analyze_current_context.assert_called_once_with(None)


def test_ai_analysis_endpoint_passes_optional_instruction() -> None:
    """Endpoint forwards the optional instruction to the AI service."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.ai.build_analyze_current_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_current_context.return_value = _analysis_response()
        mock_builder.return_value = mock_service

        response = client.post(
            "/api/v1/ai/analyze-current-context",
            json={"instruction": "Focus on recovery risk."},
        )

    assert response.status_code == 200
    mock_service.analyze_current_context.assert_called_once_with("Focus on recovery risk.")


def test_ai_analysis_endpoint_is_registered_in_openapi() -> None:
    """OpenAPI includes the AI analysis route."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/ai/analyze-current-context" in response.json()["paths"]


def test_ai_analysis_endpoint_returns_503_for_missing_configuration() -> None:
    """Endpoint translates AI configuration problems to HTTP 503."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.ai.build_analyze_current_context_service"
    ) as mock_builder:
        mock_builder.side_effect = AIConfigurationError("OPENAI_API_KEY is not configured.")

        response = client.post("/api/v1/ai/analyze-current-context")

    assert response.status_code == 503
    assert response.json() == {"detail": "OPENAI_API_KEY is not configured."}


def test_ai_analysis_endpoint_returns_503_for_provider_failure() -> None:
    """Endpoint translates provider failures to HTTP 503."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.ai.build_analyze_current_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_current_context.side_effect = AIProviderError(
            "AI provider request failed."
        )
        mock_builder.return_value = mock_service

        response = client.post("/api/v1/ai/analyze-current-context")

    assert response.status_code == 503
    assert response.json() == {"detail": "AI provider request failed."}
