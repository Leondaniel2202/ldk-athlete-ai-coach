from __future__ import annotations

from pydantic import BaseModel

from ldk_athlete_ai_coach.ai.schemas import PhaseContextAnalysisResult, WorkoutContextAnalysisResult


class AnalyzePhaseContextRequest(BaseModel):
    """Request payload for phase-context analysis."""

    instruction: str | None = None


class AnalyzePhaseContextResponse(PhaseContextAnalysisResult):
    """API response schema for current-context analysis."""


class AnalyzeWorkoutContextRequest(BaseModel):
    """Request payload for workout-context analysis."""

    instruction: str | None = None


class AnalyzeWorkoutContextResponse(WorkoutContextAnalysisResult):
    """API response schema for workout-context analysis."""
