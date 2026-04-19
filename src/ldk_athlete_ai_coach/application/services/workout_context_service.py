"""Aggregate current phase context from the local database."""

from __future__ import annotations

from datetime import UTC, datetime

from ldk_athlete_ai_coach.api.v1.schemas.common import ContextMetadataResponse
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.workout_context import WorkoutContextResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import (
    WorkoutDetailResponse,
)
from ldk_athlete_ai_coach.db.models.training import Workout
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus


class WorkoutContextService:
    """Build the workout-centric training context response.

    Orchestrates repository calls, status calculations, and data-quality checks
    to produce a ``WorkoutContextResponse`` for a single workout.
    """

    def __init__(
        self,
        workout_repository: WorkoutRepository,
        session_repository: SessionRepository,
    ) -> None:
        """Initialize the service with all required repositories.

        Args:
            workout_repository: Repository for workout lookups.
            session_repository: Repository for tracked-session lookups.
        """

        self._workout_repository: WorkoutRepository = workout_repository
        self._session_repository: SessionRepository = session_repository

    def get_specific_workout_context(self, workout_id: int) -> WorkoutContextResponse:
        """Build and return the full context snapshot for a specific training workout.

        Args:
            workout_id: Primary key of the workout to build context for.

        Returns:
            A fully populated ``WorkoutContextResponse``.

        Raises:
            ValueError: If no phase with the given ``phase_id`` exists.
        """
        as_of = datetime.now(tz=UTC)

        workout: Workout | None = self._workout_repository.get_by_id(entity_id=workout_id)
        if workout is None:
            raise ValueError("Workout not found")
        phase_summary: PhaseSummaryResponse = PhaseSummaryResponse.model_validate(workout.phase)

        metadata = ContextMetadataResponse(
            as_of_date=as_of.date(), timezone=as_of.tzname() or "UTC"
        )
        phase_summary: PhaseSummaryResponse = PhaseSummaryResponse.model_validate(workout.phase)
        plan_summary: PlanSummaryResponse | None = PlanSummaryResponse.model_validate(
            workout.phase.plan if workout.phase else None
        )

        return WorkoutContextResponse(
            metadata=metadata,
            plan_summary=plan_summary,
            phase_summary=phase_summary,
            workout_status=workout.status if workout.status else WorkoutStatus.UNKNOWN,
            workout_details=WorkoutDetailResponse.model_validate(workout),
        )
