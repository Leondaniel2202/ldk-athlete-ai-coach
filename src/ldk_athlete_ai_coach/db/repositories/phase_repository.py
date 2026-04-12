"""Repository for Phase entities."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import Phase, Workout
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository


class PhaseRepository(TrainingBaseRepository[Phase]):
    """Persistence layer for :class:`Phase` entities."""

    def __init__(self, session: Session) -> None:
        """Initialise with an active database session."""
        super().__init__(session, Phase)

    def get_workouts(self, phase_id: int) -> list[Workout]:
        """Return all workouts that belong to the given phase.

        Args:
            phase_id: Primary key of the parent phase.

        Returns:
            Ordered list of :class:`Workout` rows.

        """
        phase = self._session.get(Phase, phase_id)
        if phase is None:
            return []
        return list(phase.workouts)

    def get_active_for_plan(self, plan_id: int, now: datetime) -> Phase | None:
        """Return the active phase for the given plan at *now*."""
        stmt = (
            select(Phase)
            .where(
                and_(
                    Phase.plan_id == plan_id,
                    or_(Phase.timeframe_start.is_not(None), Phase.timeframe_end.is_not(None)),
                    or_(Phase.timeframe_start.is_(None), Phase.timeframe_start <= now),
                    or_(Phase.timeframe_end.is_(None), Phase.timeframe_end >= now),
                )
            )
            .order_by(Phase.timeframe_start.is_(None), Phase.timeframe_start.desc(), Phase.id.desc())
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def get_latest_for_plan(self, plan_id: int) -> Phase | None:
        """Return the latest phase for the given plan by timeframe start date."""
        stmt = (
            select(Phase)
            .where(Phase.plan_id == plan_id)
            .order_by(Phase.timeframe_start.is_(None), Phase.timeframe_start.desc(), Phase.id.desc())
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none()
