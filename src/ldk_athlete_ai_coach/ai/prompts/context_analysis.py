"""Shared prompt builders for AI context analysis."""

from __future__ import annotations

import json
from typing import Literal, TypedDict

from ldk_athlete_ai_coach.api.v1.schemas.phase_context import PhaseContextResponse
from ldk_athlete_ai_coach.api.v1.schemas.workout_context import WorkoutContextResponse


class PromptMessage(TypedDict):
    """Single chat message for the LLM input payload."""

    role: str
    content: str


type PromptMessages = list[PromptMessage]
type ContextKind = Literal["phase", "workout"]
type AnalysisContext = PhaseContextResponse | WorkoutContextResponse

_ANALYSIS_REQUEST_TEMPLATE = (
    "Analyze the athlete's current {context_kind} context "
    "and return a compact structured assessment."
)
_ADDITIONAL_INSTRUCTION_PREFIX = "Additional instruction: "

_SYSTEM_PROMPTS: dict[ContextKind, str] = {
    "phase": """You are an AI hybrid coach analyzing a phase snapshot.
A phase is a distinct period in the athlete's training,
typically with specific goals and characteristics.
Use only the provided context.
Do not invent missing facts.
If the context is incomplete, make that clear in your concerns or recommendation.
Keep the output concise, grounded, and structured.
Return content that matches the requested schema exactly.""",
    "workout": """You are an AI hybrid coach analyzing a workout snapshot.
A workout is a specific training session with its own goals, structure, and performance data.
Use only the provided context.
Do not invent missing facts.
If the context is incomplete, make that clear in your concerns or recommendation.
Keep the output concise, grounded, and structured.
Return content that matches the requested schema exactly.""",
}



def _serialize_context_payload(context: AnalysisContext) -> str:
    """Serialize context models with deterministic formatting for stable prompts."""
    return json.dumps(context.model_dump(mode="json"), indent=2, sort_keys=True)


def _build_user_sections(
    *,
    context_kind: ContextKind,
    payload: str,
    instruction: str | None,
) -> list[str]:
    sections = [_ANALYSIS_REQUEST_TEMPLATE.format(context_kind=context_kind)]
    if cleaned_instruction := (instruction or "").strip():
        sections.append(f"{_ADDITIONAL_INSTRUCTION_PREFIX}{cleaned_instruction}")
    sections.extend([f"{context_kind.capitalize()} context JSON:", payload])
    return sections


def build_analyze_context_prompt(
    *,
    context_kind: ContextKind,
    payload: str,
    instruction: str | None = None,
) -> PromptMessages:
    """Build deterministic model input for a context-analysis request."""
    sections = _build_user_sections(
        context_kind=context_kind,
        payload=payload,
        instruction=instruction,
    )

    return [
        {"role": "system", "content": _SYSTEM_PROMPTS[context_kind]},
        {"role": "user", "content": "\n\n".join(sections)},
    ]


def build_analyze_phase_context_prompt(
    context: PhaseContextResponse,
    instruction: str | None = None,
) -> PromptMessages:
    """Build prompt messages for phase-context analysis."""
    payload = _serialize_context_payload(context)
    return build_analyze_context_prompt(
        context_kind="phase",
        payload=payload,
        instruction=instruction,
    )


def build_analyze_workout_context_prompt(
    context: WorkoutContextResponse,
    instruction: str | None = None,
) -> PromptMessages:
    """Build prompt messages for workout-context analysis."""
    payload = _serialize_context_payload(context)
    return build_analyze_context_prompt(
        context_kind="workout",
        payload=payload,
        instruction=instruction,
    )
