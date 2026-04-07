"""Repository for Workout entities."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.sport_manager import TrackedSession, Workout
from ldk_athlete_ai_coach.db.repositories.sport_manager_base_repository import (
    SportManagerBaseRepository,
)


class WorkoutRepository(SportManagerBaseRepository[Workout]):
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
