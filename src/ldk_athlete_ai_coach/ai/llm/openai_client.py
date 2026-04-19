"""Generic OpenAI client wrapper for structured output."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from ldk_athlete_ai_coach.ai.errors import AIConfigurationError, AIProviderError

TModel = TypeVar("TModel")


class OpenAIClient:
    """Thin OpenAI wrapper that can parse structured output into a schema."""

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

    def parse_structured(self, *, messages: list[dict[str, str]], schema: Any) -> Any:
        """Call OpenAI Responses API and return parsed structured output."""
        try:
            response = self._client.responses.parse(
                model=self._model,
                input=messages,  # pyright: ignore[reportArgumentType]
                text_format=schema,
            )
        except Exception as exc:  # pragma: no cover - SDK error surface varies
            raise AIProviderError("AI provider request failed.") from exc

        parsed = response.output_parsed
        if parsed is None:
            raise AIProviderError("AI provider returned no structured output.")
        return parsed

    @staticmethod
    def validate_or_raise(parsed: Any, *, schema: type[BaseModel]) -> Any:
        """Normalize parsed output into the requested schema."""
        if isinstance(parsed, schema):
            return parsed
        try:
            return schema.model_validate(parsed)
        except ValidationError as exc:
            raise AIProviderError("AI provider returned invalid structured output.") from exc
