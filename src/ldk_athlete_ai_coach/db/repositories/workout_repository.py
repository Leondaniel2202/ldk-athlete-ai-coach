"""Repository for Workout entities."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
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

    def get_upcoming_for_phase(self, phase_id: int, now: datetime) -> list[Workout]:
        """Return upcoming workouts for the phase from *now* onward."""
        stmt = (
            select(Workout)
            .where(
                Workout.phase_id == phase_id,
                Workout.date_start.is_not(None),
                Workout.date_start >= now,
            )
            .order_by(Workout.date_start.asc(), Workout.id.asc())
        )
        return list(self._session.execute(stmt).scalars().all())

    def count_missing_scheduled_date_for_phase(self, phase_id: int) -> int:
        """Return how many workouts in the phase do not have a planned date."""
        stmt = select(func.count()).select_from(Workout).where(
            Workout.phase_id == phase_id,
            Workout.date_start.is_(None),
        )
        return int(self._session.execute(stmt).scalar_one())

    def get_recent_by_effective_date(self, since: datetime, now: datetime) -> list[Workout]:
        """Return recent workouts ordered by effective date descending."""
        effective_date = func.coalesce(Workout.done_date_start, Workout.date_start)
        stmt = (
            select(Workout)
            .where(
                effective_date.is_not(None),
                effective_date >= since,
                effective_date <= now,
            )
            .order_by(effective_date.desc(), Workout.id.desc())
        )
        return list(self._session.execute(stmt).scalars().all())

    def get_scheduled_within_window(self, since: datetime, now: datetime) -> list[Workout]:
        """Return workouts scheduled between *since* and *now* inclusive."""
        stmt = (
            select(Workout)
            .where(
                Workout.date_start.is_not(None),
                Workout.date_start >= since,
                Workout.date_start <= now,
            )
            .order_by(Workout.date_start.desc(), Workout.id.desc())
        )
        return list(self._session.execute(stmt).scalars().all())
