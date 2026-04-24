"""Service tests for AI phase-context analysis orchestration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ldk_athlete_ai_coach.ai.errors import AIProviderError
from ldk_athlete_ai_coach.ai.services.phase_context_analysis import AnalyzePhaseContextService
from ldk_athlete_ai_coach.api.v1.schemas.ai import AnalyzePhaseContextResponse

pytestmark = pytest.mark.unit

def _analysis() -> AnalyzePhaseContextResponse:
    return AnalyzePhaseContextResponse(
        summary="Context is sparse but analyzable.",
        phase_focus="Clarify the active phase.",
        positives=["The endpoint can still assess gaps."],
        concerns=["No current plan is synced."],
        recommendation="Sync the latest training plan before deeper analysis.",
    )


def _return_parsed(
    parsed: AnalyzePhaseContextResponse,
    schema: type[AnalyzePhaseContextResponse],
) -> AnalyzePhaseContextResponse:
    del schema
    return parsed


def test_service_reuses_phase_context_service_and_prompt_builder() -> None:
    """The service fetches context, builds the prompt, and calls the provider."""
    phase_context = MagicMock(name="phase_context")
    phase_context_service = MagicMock()
    phase_context_service.get_specific_phase_context.return_value = phase_context
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = _analysis()
    llm_client.validate_or_raise.side_effect = _return_parsed
    service = AnalyzePhaseContextService(phase_context_service, llm_client)

    with patch(
        "ldk_athlete_ai_coach.ai.services.phase_context_analysis.build_analyze_phase_context_prompt",
        return_value=[{"role": "system", "content": "prompt"}],
    ) as mock_prompt_builder:
        response = service.analyze_phase_context(phase_id=7, instruction="Prioritize recovery")

    assert response == _analysis()
    phase_context_service.get_specific_phase_context.assert_called_once_with(phase_id=7)
    mock_prompt_builder.assert_called_once_with(
        context=phase_context,
        instruction="Prioritize recovery",
    )
    llm_client.parse_structured.assert_called_once_with(
        messages=[{"role": "system", "content": "prompt"}],
        schema=AnalyzePhaseContextResponse,
    )


def test_service_validates_provider_output() -> None:
    """The service validates dict output from the provider through Pydantic."""
    phase_context_service = MagicMock()
    phase_context_service.get_specific_phase_context.return_value = MagicMock()
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = _analysis().model_dump(mode="json")
    llm_client.validate_or_raise.side_effect = lambda parsed, schema: schema.model_validate(parsed)
    service = AnalyzePhaseContextService(phase_context_service, llm_client)

    with patch(
        "ldk_athlete_ai_coach.ai.services.phase_context_analysis.build_analyze_phase_context_prompt",
        return_value=[{"role": "user", "content": "prompt"}],
    ):
        response = service.analyze_phase_context(phase_id=7)

    assert response == _analysis()


def test_service_handles_sparse_context_without_failing_early() -> None:
    """Sparse phase context is still passed to the prompt builder and provider."""
    sparse_context = MagicMock(name="sparse_phase_context")
    phase_context_service = MagicMock()
    phase_context_service.get_specific_phase_context.return_value = sparse_context
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = _analysis()
    llm_client.validate_or_raise.side_effect = _return_parsed
    service = AnalyzePhaseContextService(phase_context_service, llm_client)

    with patch(
        "ldk_athlete_ai_coach.ai.services.phase_context_analysis.build_analyze_phase_context_prompt",
        return_value=[{"role": "user", "content": "sparse prompt"}],
    ) as mock_prompt_builder:
        response = service.analyze_phase_context(phase_id=11)

    assert response.summary == "Context is sparse but analyzable."
    mock_prompt_builder.assert_called_once_with(
        context=sparse_context,
        instruction=None,
    )
    llm_client.parse_structured.assert_called_once_with(
        messages=[{"role": "user", "content": "sparse prompt"}],
        schema=AnalyzePhaseContextResponse,
    )


def test_service_translates_invalid_provider_output() -> None:
    """Malformed provider output is normalized to an AI provider error."""
    phase_context_service = MagicMock()
    phase_context_service.get_specific_phase_context.return_value = MagicMock()
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = {"summary": "missing required fields"}
    llm_client.validate_or_raise.side_effect = AIProviderError(
        "AI provider returned invalid structured output."
    )
    service = AnalyzePhaseContextService(phase_context_service, llm_client)

    with (
        patch(
            "ldk_athlete_ai_coach.ai.services.phase_context_analysis.build_analyze_phase_context_prompt",
            return_value=[{"role": "user", "content": "prompt"}],
        ),
        pytest.raises(
            AIProviderError,
            match=r"AI provider returned invalid structured output\.",
        ),
    ):
        service.analyze_phase_context(phase_id=7)
