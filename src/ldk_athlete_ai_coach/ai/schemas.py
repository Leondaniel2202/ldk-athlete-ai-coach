"""Shared AI-layer schemas.

Keep this module small. Prefer use-case-specific schemas in the API layer or in
dedicated service/prompt modules. Shared schemas belong here only when used by
multiple AI services.
"""

from __future__ import annotations

from pydantic import BaseModel


class PhaseContextAnalysisResult(BaseModel):
    """Structured result of phase-context AI analysis.

    This schema is used internally by the AI service layer. The API may expose a
    separate response DTO if versioning or transport concerns diverge.
    """

    summary: str
    phase_focus: str
    positives: list[str]
    concerns: list[str]
    recommendation: str
