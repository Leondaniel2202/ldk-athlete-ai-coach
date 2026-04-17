"""Service for AI phase analysis (placeholder).

This module is reserved for the upcoming \"analyze specific phase\" use case.
"""

from __future__ import annotations

from ldk_athlete_ai_coach.ai.llm.openai_client import OpenAIClient
from ldk_athlete_ai_coach.ai.prompts.phase_context import build_analyze_phase_context_prompt
from ldk_athlete_ai_coach.api.v1.schemas.ai import AnalyzeCurrentContextResponse
from ldk_athlete_ai_coach.application.services.phase_context_service import PhaseContextService


class AnalyzePhaseContextService:
    """Placeholder service for analyzing a specific phase."""

    def __init__(
        self,
        phase_context_service: PhaseContextService,
        llm_client: OpenAIClient,
    ) -> None:
        self.phase_context_service = phase_context_service
        self._llm = llm_client

    def analyze_phase_context(
        self, phase_id: int, instruction: str | None = None
    ) -> AnalyzeCurrentContextResponse:
        context = self.phase_context_service.get_specific_phase_context(phase_id=phase_id)
        messages = build_analyze_phase_context_prompt(context, instruction)
        parsed = self._llm.parse_structured(messages=messages, schema=AnalyzeCurrentContextResponse)
        return self._llm.validate_or_raise(parsed, schema=AnalyzeCurrentContextResponse)
