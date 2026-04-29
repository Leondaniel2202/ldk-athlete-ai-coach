"""Repository for Workout entities."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import Workout
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus
from ldk_athlete_ai_coach.utils.date_utils import get_week_start_for_date


class WorkoutRepository(TrainingBaseRepository[Workout]):
    """Persistence layer for :class:`Workout` entities."""

    def __init__(self, session: Session) -> None:
        """Initialise with an active database session."""
        super().__init__(session, Workout)

    def list_by_phase_id(
        self,
        phase_id: int,
        *,
        status: WorkoutStatus | None = None,
    ) -> list[Workout]:
        """Return all workouts for the given phase."""
        conditions = [Workout.phase_id == phase_id]
        if status is not None:
            conditions.append(Workout.status == status)
        stmt = select(Workout).where(*conditions)
        return list(self._session.execute(stmt).scalars().all())

    def list_upcoming_by_phase_id(self, phase_id: int, now: datetime) -> list[Workout]:
        """Return upcoming workouts for the phase from *now* onward."""
        effective_date = func.coalesce(Workout.done_date_start, Workout.date_start)
        stmt = (
            select(Workout)
            .where(
                Workout.phase_id == phase_id,
                Workout.planned_week_start_date >= get_week_start_for_date(now),
                effective_date >= now,
            )
            .order_by(Workout.date_start.asc(), Workout.id.asc())
        )
        return list(self._session.execute(stmt).scalars().all())

    def list_within_planned_week(
        self,
        week_start_date: datetime,
        phase_filter: Literal["with_phase", "without_phase", "all"] = "all",
    ) -> list[Workout]:
        """Return workouts in the given phase with the given planned_week_start_date."""
        # Normalise to midnight so the equality matches dates stored from Notion.
        normalised = week_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        conditions = [Workout.planned_week_start_date == normalised]
        if phase_filter == "with_phase":
            conditions.append(Workout.phase_id.is_not(None))
        elif phase_filter == "without_phase":
            conditions.append(Workout.phase_id.is_(None))
        stmt = select(Workout).where(*conditions).order_by(Workout.id.desc())
        return list(self._session.execute(stmt).scalars().all())

    def count_unscheduled_by_phase_id(self, phase_id: int) -> int:
        """Return how many workouts in the phase do not have a planned date."""
        stmt = (
            select(func.count())
            .select_from(Workout)
            .where(
                Workout.phase_id == phase_id,
                Workout.date_start.is_(None),
            )
        )
        return int(self._session.execute(stmt).scalar_one())
