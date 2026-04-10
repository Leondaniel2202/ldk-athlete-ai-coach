"""Repository for Workout entities."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import TrackedSession, Workout
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository


class WorkoutRepository(TrainingBaseRepository[Workout]):
    """Persistence layer for :class:`Workout` entities."""

    def __init__(self, session: Session) -> None:
        """Initialise with an active database session."""
        super().__init__(session, Workout)

    def get_sessions(self, workout_id: int) -> list[TrackedSession]:
        """Return all tracked sessions linked to the given workout.

        Args:
            workout_id: Primary key of the parent workout.

        Returns:
            List of :class:`TrackedSession` rows.
        """
        workout = self._session.get(Workout, workout_id)
        if workout is None:
            return []
        return list(workout.tracked_sessions)
