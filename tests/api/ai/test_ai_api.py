"""API tests for the AI analysis endpoints."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ldk_athlete_ai_coach.ai.errors import AIConfigurationError, AIProviderError
from ldk_athlete_ai_coach.api.v1.schemas.ai import (
    AnalyzePhaseContextResponse,
    AnalyzeWorkoutContextResponse,
)

pytestmark = pytest.mark.api


def _phase_analysis_response() -> AnalyzePhaseContextResponse:
    return AnalyzePhaseContextResponse(
        summary="Current phase context looks coherent.",
        phase_focus="Build race-specific durability.",
        positives=["Workouts are aligned with the phase."],
        concerns=["Recent intensity may be clustered."],
        recommendation="Keep the current direction and protect recovery.",
    )


def _workout_analysis_response() -> AnalyzeWorkoutContextResponse:
    return AnalyzeWorkoutContextResponse(
        summary="This workout fits the current phase.",
        workout_focus="Protect the recovery demand from the intensity.",
        positives=["The workout is specific to the target demand."],
        concerns=["Execution quality may depend on freshness."],
        recommendation="Keep the structure and monitor post-session recovery.",
    )


def test_phase_analysis_endpoint_returns_structured_response(app_client: TestClient) -> None:
    """Endpoint returns a compact structured AI phase assessment on success."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_phase_context.return_value = _phase_analysis_response()
        mock_builder.return_value = mock_service

        response = app_client.post("/api/v1/ai/analysis/specific-phase-context/42")

    assert response.status_code == 200
    assert response.json() == _phase_analysis_response().model_dump(mode="json")
    assert mock_builder.call_args.kwargs["context"] == "phase_context"
    mock_service.analyze_phase_context.assert_called_once_with(phase_id=42, instruction=None)


def test_phase_analysis_endpoint_accepts_empty_json_body(app_client: TestClient) -> None:
    """Endpoint treats {} the same as an omitted request body."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_phase_context.return_value = _phase_analysis_response()
        mock_builder.return_value = mock_service

        response = app_client.post("/api/v1/ai/analysis/specific-phase-context/42", json={})

    assert response.status_code == 200
    mock_service.analyze_phase_context.assert_called_once_with(phase_id=42, instruction=None)


def test_phase_analysis_endpoint_passes_optional_instruction(app_client: TestClient) -> None:
    """Endpoint forwards the optional instruction to the AI service."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_phase_context.return_value = _phase_analysis_response()
        mock_builder.return_value = mock_service

        response = app_client.post(
            "/api/v1/ai/analysis/specific-phase-context/42",
            json={"instruction": "Focus on recovery risk."},
        )

    assert response.status_code == 200
    mock_service.analyze_phase_context.assert_called_once_with(
        phase_id=42,
        instruction="Focus on recovery risk.",
    )


def test_phase_analysis_endpoint_returns_503_for_missing_configuration(
    app_client: TestClient,
) -> None:
    """Endpoint translates AI configuration problems to HTTP 503."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_builder.side_effect = AIConfigurationError("OPENAI_API_KEY is not configured.")

        response = app_client.post("/api/v1/ai/analysis/specific-phase-context/42")

    assert response.status_code == 503
    assert response.json() == {"detail": "OPENAI_API_KEY is not configured."}


def test_phase_analysis_endpoint_returns_503_for_provider_failure(
    app_client: TestClient,
) -> None:
    """Endpoint translates provider failures to HTTP 503."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_phase_context.side_effect = AIProviderError(
            "AI provider request failed."
        )
        mock_builder.return_value = mock_service

        response = app_client.post("/api/v1/ai/analysis/specific-phase-context/42")

    assert response.status_code == 503
    assert response.json() == {"detail": "AI provider request failed."}


def test_workout_analysis_endpoint_returns_structured_response(app_client: TestClient) -> None:
    """Endpoint returns a compact structured AI workout assessment on success."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_specific_workout_context.return_value = _workout_analysis_response()
        mock_builder.return_value = mock_service

        response = app_client.post("/api/v1/ai/analysis/specific-workout-context/24")

    assert response.status_code == 200
    assert response.json() == _workout_analysis_response().model_dump(mode="json")
    assert mock_builder.call_args.kwargs["context"] == "workout_context"
    mock_service.analyze_specific_workout_context.assert_called_once_with(
        workout_id=24,
        instruction=None,
    )


def test_workout_analysis_endpoint_accepts_empty_json_body(app_client: TestClient) -> None:
    """Workout endpoint treats {} the same as an omitted request body."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_specific_workout_context.return_value = _workout_analysis_response()
        mock_builder.return_value = mock_service

        response = app_client.post("/api/v1/ai/analysis/specific-workout-context/24", json={})

    assert response.status_code == 200
    mock_service.analyze_specific_workout_context.assert_called_once_with(
        workout_id=24,
        instruction=None,
    )


def test_workout_analysis_endpoint_passes_optional_instruction(app_client: TestClient) -> None:
    """Workout endpoint forwards the optional instruction to the AI service."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_specific_workout_context.return_value = _workout_analysis_response()
        mock_builder.return_value = mock_service

        response = app_client.post(
            "/api/v1/ai/analysis/specific-workout-context/24",
            json={"instruction": "Focus on fueling execution."},
        )

    assert response.status_code == 200
    mock_service.analyze_specific_workout_context.assert_called_once_with(
        workout_id=24,
        instruction="Focus on fueling execution.",
    )


def test_workout_analysis_endpoint_returns_503_for_missing_configuration(
    app_client: TestClient,
) -> None:
    """Workout endpoint translates AI configuration problems to HTTP 503."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_builder.side_effect = AIConfigurationError("OPENAI_API_KEY is not configured.")

        response = app_client.post("/api/v1/ai/analysis/specific-workout-context/24")

    assert response.status_code == 503
    assert response.json() == {"detail": "OPENAI_API_KEY is not configured."}


def test_workout_analysis_endpoint_returns_503_for_provider_failure(
    app_client: TestClient,
) -> None:
    """Workout endpoint translates provider failures to HTTP 503."""
    with patch(
        "ldk_athlete_ai_coach.api.v1.routers.ai.analysis.build_analyze_context_service"
    ) as mock_builder:
        mock_service = MagicMock()
        mock_service.analyze_specific_workout_context.side_effect = AIProviderError(
            "AI provider request failed."
        )
        mock_builder.return_value = mock_service

        response = app_client.post("/api/v1/ai/analysis/specific-workout-context/24")

    assert response.status_code == 503
    assert response.json() == {"detail": "AI provider request failed."}


def test_ai_analysis_routes_are_registered_in_openapi(app_client: TestClient) -> None:
    """OpenAPI includes both AI analysis routes."""
    response = app_client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/ai/analysis/specific-phase-context/{phase_id}" in paths
    assert "/api/v1/ai/analysis/specific-workout-context/{workout_id}" in paths
