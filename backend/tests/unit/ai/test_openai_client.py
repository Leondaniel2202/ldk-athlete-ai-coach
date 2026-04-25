"""Unit tests for OpenAI client wrapper behavior."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from ldk_athlete_ai_coach.ai.errors import AIConfigurationError, AIProviderError
from ldk_athlete_ai_coach.ai.llm.openai_client import OpenAIClient
from ldk_athlete_ai_coach.ai.prompts.context_analysis import PromptMessage

pytestmark = pytest.mark.unit


class _AnalysisSchema(BaseModel):
    summary: str


class _FakeResponses:
    def __init__(self, parsed: object = None, should_raise: bool = False) -> None:
        self._parsed = parsed
        self._should_raise = should_raise

    def parse(self, **kwargs: object) -> SimpleNamespace:
        if self._should_raise:
            raise RuntimeError("provider failure")
        return SimpleNamespace(output_parsed=self._parsed, call_kwargs=kwargs)


class _FakeOpenAI:
    def __init__(self, *, api_key: str, timeout: int) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.responses = _FakeResponses()


def _install_fake_openai(monkeypatch: pytest.MonkeyPatch, fake_openai_cls: type) -> None:
    fake_module = SimpleNamespace(OpenAI=fake_openai_cls)
    monkeypatch.setitem(sys.modules, "openai", fake_module)


def test_init_requires_api_key() -> None:
    with pytest.raises(AIConfigurationError, match="OPENAI_API_KEY is not configured"):
        OpenAIClient(api_key=None, model="gpt-4o-mini", timeout_seconds=15)


def test_parse_structured_calls_responses_api_and_returns_parsed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parsed = _AnalysisSchema(summary="Structured response")

    class _SuccessfulOpenAI(_FakeOpenAI):
        def __init__(self, *, api_key: str, timeout: int) -> None:
            super().__init__(api_key=api_key, timeout=timeout)
            self.responses = _FakeResponses(parsed=parsed)

    _install_fake_openai(monkeypatch, _SuccessfulOpenAI)
    client = OpenAIClient(api_key="test-key", model="gpt-4o-mini", timeout_seconds=30)

    messages: PromptMessage = PromptMessage({"role": "system", "content": "Analyze context."})
    result = client.parse_structured(messages=[messages], schema=_AnalysisSchema)

    assert result == parsed


def test_parse_structured_raises_when_provider_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_openai(monkeypatch, _FakeOpenAI)
    client = OpenAIClient(api_key="test-key", model="gpt-4o-mini", timeout_seconds=30)

    with pytest.raises(AIProviderError, match="returned no structured output"):
        client.parse_structured(
            messages=[{"role": "user", "content": "hello"}],
            schema=_AnalysisSchema,
        )


def test_parse_structured_translates_provider_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FailingOpenAI(_FakeOpenAI):
        def __init__(self, *, api_key: str, timeout: int) -> None:
            super().__init__(api_key=api_key, timeout=timeout)
            self.responses = _FakeResponses(should_raise=True)

    _install_fake_openai(monkeypatch, _FailingOpenAI)
    client = OpenAIClient(api_key="test-key", model="gpt-4o-mini", timeout_seconds=30)

    with pytest.raises(AIProviderError, match="AI provider request failed"):
        client.parse_structured(
            messages=[{"role": "user", "content": "hello"}],
            schema=_AnalysisSchema,
        )


def test_validate_or_raise_returns_existing_schema_instance() -> None:
    parsed = _AnalysisSchema(summary="Looks good")

    result = OpenAIClient.validate_or_raise(parsed, schema=_AnalysisSchema)

    assert result is parsed


def test_validate_or_raise_validates_dict_into_schema() -> None:
    parsed = {"summary": "Looks good"}

    result = OpenAIClient.validate_or_raise(parsed, schema=_AnalysisSchema)

    assert result == _AnalysisSchema(summary="Looks good")


def test_validate_or_raise_translates_validation_error() -> None:
    parsed = {"missing": "field"}

    with pytest.raises(AIProviderError, match="invalid structured output"):
        OpenAIClient.validate_or_raise(parsed, schema=_AnalysisSchema)
