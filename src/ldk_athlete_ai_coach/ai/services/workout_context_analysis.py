"""Service for AI workout analysis (placeholder).

This module is reserved for the upcoming "analyze specific workout" use case.
"""

from __future__ import annotations

from ldk_athlete_ai_coach.ai.llm.openai_client import OpenAIClient
from ldk_athlete_ai_coach.ai.prompts.context_analysis import (
    PromptMessage,
    build_analyze_workout_context_prompt,
)
from ldk_athlete_ai_coach.api.v1.schemas.ai import AnalyzeWorkoutContextResponse
from ldk_athlete_ai_coach.api.v1.schemas.workout_context import WorkoutContextResponse
from ldk_athlete_ai_coach.application.services.workout_context_service import WorkoutContextService


class AnalyzeWorkoutContextService:
    """Placeholder service for analyzing a specific workout."""

    def __init__(
        self,
        workout_context_service: WorkoutContextService,
        llm_client: OpenAIClient,
    ) -> None:
        self.workout_context_service = workout_context_service
        self._llm = llm_client

    def analyze_specific_workout_context(
        self, workout_id: int, instruction: str | None = None
    ) -> AnalyzeWorkoutContextResponse:
        context: WorkoutContextResponse = self.workout_context_service.get_specific_workout_context(workout_id=workout_id)
        messages: list[PromptMessage] = build_analyze_workout_context_prompt(context=context, instruction=instruction)
        parsed: AnalyzeWorkoutContextResponse = self._llm.parse_structured(
            messages=messages,
            schema=AnalyzeWorkoutContextResponse,
        )
        return self._llm.validate_or_raise(
            parsed=parsed,
            schema=AnalyzeWorkoutContextResponse,
        )
