from __future__ import annotations

from pydantic import BaseModel

from ldk_athlete_ai_coach.ai.schemas import CurrentContextAnalysisResult


class AnalyzeCurrentContextRequest(BaseModel):
    """Request payload for current-context analysis."""

    instruction: str | None = None


class AnalyzeCurrentContextResponse(CurrentContextAnalysisResult):
    """API response schema for current-context analysis."""