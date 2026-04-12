"""Provider abstraction and OpenAI implementation for AI analysis."""

from __future__ import annotations

from typing import Protocol

from pydantic import ValidationError

from ldk_athlete_ai_coach.ai.errors import AIConfigurationError, AIProviderError
from ldk_athlete_ai_coach.ai.prompt_builder import PromptMessages
from ldk_athlete_ai_coach.api.v1.schemas.ai import AnalyzeCurrentContextResponse


class AnalyzeCurrentContextProvider(Protocol):
    """Provider interface for current-context analysis."""

    def analyze(
        self,
        prompt_messages: PromptMessages,
    ) -> AnalyzeCurrentContextResponse | dict[str, object]:
        """Return a compact structured analysis for the supplied prompt."""


class OpenAIAnalyzeCurrentContextProvider:
    """OpenAI-backed provider for current-context analysis."""

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        timeout_seconds: int,
    ) -> None:
        if not api_key:
            raise AIConfigurationError("OPENAI_API_KEY is not configured.")
        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise AIConfigurationError("OpenAI SDK is not installed.") from exc

        self._client = OpenAI(api_key=api_key, timeout=timeout_seconds)
        self._model = model

    def analyze(
        self,
        prompt_messages: PromptMessages,
    ) -> AnalyzeCurrentContextResponse:
        """Call the OpenAI Responses API and validate the structured output."""
        try:
            response = self._client.responses.parse(
                model=self._model,
                input=prompt_messages,
                text_format=AnalyzeCurrentContextResponse,
            )
        except Exception as exc:  # pragma: no cover - SDK error surface varies
            raise AIProviderError("AI provider request failed.") from exc

        parsed = response.output_parsed
        if parsed is None:
            raise AIProviderError("AI provider returned no structured output.")
        if isinstance(parsed, AnalyzeCurrentContextResponse):
            return parsed
        try:
            return AnalyzeCurrentContextResponse.model_validate(parsed)
        except ValidationError as exc:
            raise AIProviderError("AI provider returned invalid structured output.") from exc
