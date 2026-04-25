"""Service tests for AI workout-context analysis orchestration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ldk_athlete_ai_coach.ai.errors import AIProviderError
from ldk_athlete_ai_coach.ai.services.workout_context_analysis import AnalyzeWorkoutContextService
from ldk_athlete_ai_coach.api.v1.schemas.ai import AnalyzeWorkoutContextResponse

pytestmark = pytest.mark.unit


def _analysis() -> AnalyzeWorkoutContextResponse:
    return AnalyzeWorkoutContextResponse(
        summary="The workout is analyzable.",
        workout_focus="Keep the demand specific to the target adaptation.",
        positives=["The structure is coherent."],
        concerns=["Recovery may constrain execution quality."],
        recommendation="Keep the main set and monitor the recovery response.",
    )


def _return_parsed(
    parsed: AnalyzeWorkoutContextResponse,
    schema: type[AnalyzeWorkoutContextResponse],
) -> AnalyzeWorkoutContextResponse:
    del schema
    return parsed


def test_service_reuses_workout_context_service_and_prompt_builder() -> None:
    """The service fetches context, builds the prompt, and calls the provider."""
    workout_context = MagicMock(name="workout_context")
    workout_context_service = MagicMock()
    workout_context_service.get_specific_workout_context.return_value = workout_context
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = _analysis()
    llm_client.validate_or_raise.side_effect = _return_parsed
    service = AnalyzeWorkoutContextService(workout_context_service, llm_client)

    with patch(
        "ldk_athlete_ai_coach.ai.services.workout_context_analysis.build_analyze_workout_context_prompt",
        return_value=[{"role": "system", "content": "prompt"}],
    ) as mock_prompt_builder:
        response = service.analyze_specific_workout_context(
            workout_id=12,
            instruction="Focus on execution quality",
        )

    assert response == _analysis()
    workout_context_service.get_specific_workout_context.assert_called_once_with(workout_id=12)
    mock_prompt_builder.assert_called_once_with(
        context=workout_context,
        instruction="Focus on execution quality",
    )
    llm_client.parse_structured.assert_called_once_with(
        messages=[{"role": "system", "content": "prompt"}],
        schema=AnalyzeWorkoutContextResponse,
    )


def test_service_validates_provider_output() -> None:
    """The service validates dict output from the provider through Pydantic."""
    workout_context_service = MagicMock()
    workout_context_service.get_specific_workout_context.return_value = MagicMock()
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = _analysis().model_dump(mode="json")
    llm_client.validate_or_raise.side_effect = lambda parsed, schema: schema.model_validate(parsed)
    service = AnalyzeWorkoutContextService(workout_context_service, llm_client)

    with patch(
        "ldk_athlete_ai_coach.ai.services.workout_context_analysis.build_analyze_workout_context_prompt",
        return_value=[{"role": "user", "content": "prompt"}],
    ):
        response = service.analyze_specific_workout_context(workout_id=12)

    assert response == _analysis()


def test_service_translates_invalid_provider_output() -> None:
    """Malformed provider output is normalized to an AI provider error."""
    workout_context_service = MagicMock()
    workout_context_service.get_specific_workout_context.return_value = MagicMock()
    llm_client = MagicMock()
    llm_client.parse_structured.return_value = {"summary": "missing required fields"}
    llm_client.validate_or_raise.side_effect = AIProviderError(
        "AI provider returned invalid structured output."
    )
    service = AnalyzeWorkoutContextService(workout_context_service, llm_client)

    with (
        patch(
            "ldk_athlete_ai_coach.ai.services.workout_context_analysis.build_analyze_workout_context_prompt",
            return_value=[{"role": "user", "content": "prompt"}],
        ),
        pytest.raises(
            AIProviderError,
            match=r"AI provider returned invalid structured output\.",
        ),
    ):
        service.analyze_specific_workout_context(workout_id=12)
