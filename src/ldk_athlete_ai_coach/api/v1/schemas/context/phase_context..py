"""Pydantic response models for the training domain."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from ldk_athlete_ai_coach.api.v1.schemas.adherence import AdherenceSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import WorkoutContentResponse, WorkoutDetailResponse
from ldk_athlete_ai_coach.domain.enums.status import PhaseStatus


class PhaseContextMetadataResponse(BaseModel):
    """Response metadata for the training-context endpoint."""

    as_of_date: date
    timezone: str
    phase_status: PhaseStatus

class PhaseContextResponse(BaseModel):
    """Response schema for a specific phase training context."""
    
    metadata: PhaseContextMetadataResponse
    phase: PhaseResponse
    open_workouts: list[WorkoutContentResponse]
    done_workouts: list[WorkoutDetailResponse]
    adherence: AdherenceSummaryResponse
    data_gaps: list[str]