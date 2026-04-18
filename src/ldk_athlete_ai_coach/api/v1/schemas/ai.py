from __future__ import annotations

from pydantic import BaseModel

from ldk_athlete_ai_coach.ai.schemas import PhaseContextAnalysisResult


class AnalyzePhaseContextRequest(BaseModel):
    """Request payload for phase-context analysis."""

    instruction: str | None = None


class AnalyzePhaseContextResponse(PhaseContextAnalysisResult):
    """API response schema for current-context analysis."""
