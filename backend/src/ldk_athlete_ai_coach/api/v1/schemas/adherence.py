"""Pydantic response models for the training domain."""

from __future__ import annotations

from pydantic import BaseModel


class WorkoutAdherenceSummaryResponse(BaseModel):
    """Summary of workout adherence in a reporting window."""

    planned_workouts: int
    completed_workouts: int
    skipped_workouts: int
    unknown_workouts: int
    completion_ratio: float | None
