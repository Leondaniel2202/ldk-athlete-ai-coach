"""Repository for Phase entities."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import Phase
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository


class PhaseRepository(TrainingBaseRepository[Phase]):
    """Persistence layer for :class:`Phase` entities."""

    def __init__(self, session: Session) -> None:
        """Initialise with an active database session."""
        super().__init__(session, Phase)

    def get_active_for_datetime(self, now: datetime) -> Phase | None:
        """Return the active phase at *now*."""
        today = now.date()
        stmt = (
            select(Phase)
            .where(
                and_(
                    Phase.start_date <= today,
                    Phase.end_date >= today,
                )
            )
            .order_by(Phase.start_date.desc(), Phase.id.desc())
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def get_by_date(self, date: datetime) -> Phase | None:
        """Return the phase active at the given date, or ``None`` if no such phase exists.

        If multiple phases match, return the one with the latest timeframe start date.
        """
        day = date.date()
        stmt = (
            select(Phase)
            .where(
                and_(
                    Phase.start_date <= day,
                    Phase.end_date >= day,
                )
            )
            .order_by(Phase.start_date.desc(), Phase.id.desc())
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def get_latest_by_plan_id(self, plan_id: int) -> Phase | None:
        """Return the latest phase for the given plan by timeframe start date."""
        stmt = (
            select(Phase)
            .where(Phase.plan_id == plan_id)
            .order_by(Phase.start_date.desc(), Phase.id.desc())
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def list_by_plan_id(self, plan_id: int) -> list[Phase]:
        """Return all phases for the given plan."""
        stmt = select(Phase).where(Phase.plan_id == plan_id)
        return list(self._session.execute(stmt).scalars().all())

    def list_by_timeframe_window(self, start: datetime, end: datetime) -> list[Phase]:
        """Return all phases with any overlap with the given timeframe window."""
        start_date = start.date()
        end_date = end.date()
        stmt = (
            select(Phase)
            .where(
                and_(
                    Phase.start_date <= end_date,
                    Phase.end_date >= start_date,
                )
            )
            .order_by(Phase.start_date.asc(), Phase.id.asc())
        )
        return list(self._session.execute(stmt).scalars().all())
