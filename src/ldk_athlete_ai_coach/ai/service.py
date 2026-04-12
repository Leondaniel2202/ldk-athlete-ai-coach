"""AI orchestration service for current-context analysis."""

from __future__ import annotations

from pydantic import ValidationError

from ldk_athlete_ai_coach.ai.errors import AIProviderError
from ldk_athlete_ai_coach.ai.prompt_builder import build_analyze_current_context_prompt
from ldk_athlete_ai_coach.ai.provider import AnalyzeCurrentContextProvider
from ldk_athlete_ai_coach.api.v1.schemas.ai import AnalyzeCurrentContextResponse
from ldk_athlete_ai_coach.domain.training_context_service import TrainingContextService


class AnalyzeCurrentContextService:
    """Fetch training context, build prompt input, and orchestrate provider calls."""

    def __init__(
        self,
        training_context_service: TrainingContextService,
        provider: AnalyzeCurrentContextProvider,
    ) -> None:
        self._training_context_service = training_context_service
        self._provider = provider

    def analyze_current_context(
        self,
        instruction: str | None = None,
    ) -> AnalyzeCurrentContextResponse:
        """Return a compact structured analysis of the current training context."""
        context = self._training_context_service.get_current_context()
        prompt_messages = build_analyze_current_context_prompt(context, instruction)
        response = self._provider.analyze(prompt_messages)
        try:
            return AnalyzeCurrentContextResponse.model_validate(response)
        except ValidationError as exc:
            raise AIProviderError("AI provider returned invalid structured output.") from exc
