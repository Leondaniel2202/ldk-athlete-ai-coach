"""Service layer for Workout domain operations."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.sport_manager import TrackedSession, Workout
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository


class WorkoutService:
    """Provide business-logic operations for :class:`Workout` entities.

    Attributes:
        _repo: Underlying :class:`WorkoutRepository` instance.
    """

    def __init__(self, session: Session) -> None:
        """Initialise the service with an active database session.

        Args:
            session: Active SQLAlchemy session.
        """
        self._repo = WorkoutRepository(session)

    def get_workout(self, workout_id: int) -> Workout | None:
        """Return the workout with the given ID, or ``None``.

        Args:
            workout_id: Primary key of the workout.

        Returns:
            :class:`Workout` instance, or ``None`` if not found.
        """
        return self._repo.get_by_id(workout_id)

    def get_workout_sessions(self, workout_id: int) -> list[TrackedSession]:
        """Return all tracked sessions linked to the given workout.

        Args:
            workout_id: Primary key of the workout.

        Returns:
            List of :class:`TrackedSession` instances.
        """
        return self._repo.get_sessions(workout_id)
