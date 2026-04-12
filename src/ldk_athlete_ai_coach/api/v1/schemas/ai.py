"""Pydantic request/response schemas for AI endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class AnalyzeCurrentContextRequest(BaseModel):
    """Request payload for current-context analysis."""

    instruction: str | None = None


class AnalyzeCurrentContextResponse(BaseModel):
    """Compact structured AI analysis of the current training context."""

    summary: str
    phase_focus: str
    positives: list[str]
    concerns: list[str]
    recommendation: str
