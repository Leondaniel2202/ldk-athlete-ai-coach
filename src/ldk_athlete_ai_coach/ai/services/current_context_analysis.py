"""Service for AI current-context analysis.

This service orchestrates:
domain context retrieval → prompt construction → LLM call → schema validation.
"""

from __future__ import annotations

from ldk_athlete_ai_coach.ai.llm.openai_client import OpenAIClient
from ldk_athlete_ai_coach.ai.prompts.current_context import build_analyze_current_context_prompt
from ldk_athlete_ai_coach.api.v1.schemas.ai import AnalyzeCurrentContextResponse
from ldk_athlete_ai_coach.domain.services.training_context_service import TrainingContextService


class AnalyzeCurrentContextService:
    """Fetch training context, build prompt input, and call the LLM."""

    def __init__(
        self,
        training_context_service: TrainingContextService,
        llm_client: OpenAIClient,
    ) -> None:
        self._training_context_service = training_context_service
        self._llm = llm_client

    def analyze_current_context(
        self, instruction: str | None = None
    ) -> AnalyzeCurrentContextResponse:
        context = self._training_context_service.get_current_context()
        messages = build_analyze_current_context_prompt(context, instruction)
        parsed = self._llm.parse_structured(messages=messages, schema=AnalyzeCurrentContextResponse)
        return self._llm.validate_or_raise(parsed, schema=AnalyzeCurrentContextResponse)

