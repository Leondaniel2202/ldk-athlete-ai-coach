"""Service tests for AI current-context analysis orchestration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ldk_athlete_ai_coach.ai.errors import AIProviderError
from ldk_athlete_ai_coach.ai.services.current_context_analysis import (
    AnalyzeCurrentContextService,
)
from ldk_athlete_ai_coach.api.v1.schemas.ai import AnalyzeCurrentContextResponse
from ldk_athlete_ai_coach.api.v1.schemas.training import (
    AdherenceSummaryResponse,
    CurrentTrainingContextResponse,
    TrainingContextMetadataResponse,
    TrainingContextResponse,
)


def _context() -> TrainingContextResponse:
    return TrainingContextResponse(
        metadata=TrainingContextMetadataResponse(as_of_date="2026-04-12", timezone="UTC"),
        current=CurrentTrainingContextResponse(plan=None, phase=None, current_phase_week=None),
        planned_workouts=[],
        recent_workouts=[],
        adherence=AdherenceSummaryResponse(
            planned_workouts=0,
            completed_workouts=0,
            skipped_workouts=0,
            completion_ratio=None,
        ),
        data_gaps=["No plan data is available."],
    )


def _analysis() -> AnalyzeCurrentContextResponse:
    return AnalyzeCurrentContextResponse(
        summary="Context is sparse but analyzable.",
        phase_focus="Clarify the active phase.",
        positives=["The endpoint can still assess gaps."],
        concerns=["No current plan is synced."],
        recommendation="Sync the latest training plan before deeper analysis.",
    )


def test_service_reuses_training_context_service_and_prompt_builder() -> None:
    """The service fetches context, builds the prompt, and calls the provider."""
    training_context_service = MagicMock()
    training_context_service.get_current_context.return_value = _context()
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = _analysis()
    llm_client.validate_or_raise.side_effect = lambda parsed, schema: parsed
    service = AnalyzeCurrentContextService(training_context_service, llm_client)

    with patch(
        "ldk_athlete_ai_coach.ai.services.current_context_analysis.build_analyze_current_context_prompt",
        return_value=[{"role": "system", "content": "prompt"}],
    ) as mock_prompt_builder:
        response = service.analyze_current_context("Prioritize recovery")

    assert response == _analysis()
    training_context_service.get_current_context.assert_called_once_with()
    mock_prompt_builder.assert_called_once_with(_context(), "Prioritize recovery")
    llm_client.parse_structured.assert_called_once_with(
        messages=[{"role": "system", "content": "prompt"}],
        schema=AnalyzeCurrentContextResponse,
    )


def test_service_validates_provider_output() -> None:
    """The service validates dict output from the provider through Pydantic."""
    training_context_service = MagicMock()
    training_context_service.get_current_context.return_value = _context()
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = _analysis().model_dump(mode="json")
    llm_client.validate_or_raise.side_effect = (
        lambda parsed, schema: schema.model_validate(parsed)
    )
    service = AnalyzeCurrentContextService(training_context_service, llm_client)

    with patch(
        "ldk_athlete_ai_coach.ai.services.current_context_analysis.build_analyze_current_context_prompt",
        return_value=[{"role": "user", "content": "prompt"}],
    ):
        response = service.analyze_current_context()

    assert response == _analysis()


def test_service_handles_sparse_context_without_failing_early() -> None:
    """Sparse training context is still passed to the prompt builder and provider."""
    sparse_context = _context()
    training_context_service = MagicMock()
    training_context_service.get_current_context.return_value = sparse_context
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = _analysis()
    llm_client.validate_or_raise.side_effect = lambda parsed, schema: parsed
    service = AnalyzeCurrentContextService(training_context_service, llm_client)

    with patch(
        "ldk_athlete_ai_coach.ai.services.current_context_analysis.build_analyze_current_context_prompt",
        return_value=[{"role": "user", "content": "sparse prompt"}],
    ) as mock_prompt_builder:
        response = service.analyze_current_context()

    assert response.summary == "Context is sparse but analyzable."
    mock_prompt_builder.assert_called_once_with(sparse_context, None)
    llm_client.parse_structured.assert_called_once_with(
        messages=[{"role": "user", "content": "sparse prompt"}],
        schema=AnalyzeCurrentContextResponse,
    )


def test_service_translates_invalid_provider_output() -> None:
    """Malformed provider output is normalized to an AI provider error."""
    training_context_service = MagicMock()
    training_context_service.get_current_context.return_value = _context()
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = {"summary": "missing required fields"}
    llm_client.validate_or_raise.side_effect = AIProviderError(
        "AI provider returned invalid structured output."
    )
    service = AnalyzeCurrentContextService(training_context_service, llm_client)

    with patch(
        "ldk_athlete_ai_coach.ai.services.current_context_analysis.build_analyze_current_context_prompt",
        return_value=[{"role": "user", "content": "prompt"}],
    ):
        with pytest.raises(AIProviderError, match="AI provider returned invalid structured output."):
            service.analyze_current_context()
