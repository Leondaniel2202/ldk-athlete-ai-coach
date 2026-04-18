"""Prompt builder for phase analysis (placeholder).

This module is reserved for the upcoming \"analyze specific phase\" use case.
"""

from __future__ import annotations

import json

from ldk_athlete_ai_coach.api.v1.schemas.phase_context import PhaseContextResponse

PromptMessages = list[dict[str, str]]

_SYSTEM_PROMPT = """You are an AI hybrid coach analyzing a phase snapshot.
A phase is a distinct period in the athlete's training, 
typically with specific goals and characteristics.
Use only the provided context.
Do not invent missing facts.
If the context is incomplete, make that clear in your concerns or recommendation.
Keep the output concise, grounded, and structured.
Return content that matches the requested schema exactly."""


def build_analyze_phase_context_prompt(
    context: PhaseContextResponse,
    instruction: str | None = None,
) -> PromptMessages:
    """Build deterministic model input for phase-context analysis."""
    payload = json.dumps(context.model_dump(mode="json"), indent=2)
    instruction_text = instruction.strip() if instruction else ""
    user_sections = [
        "Analyze the athlete's current phase context and return a compact structured assessment.",
    ]
    if instruction_text:
        user_sections.append(f"Additional instruction: {instruction_text}")
    user_sections.extend(
        [
            "Phase context JSON:",
            payload,
        ]
    )
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": "\n\n".join(user_sections)},
    ]
