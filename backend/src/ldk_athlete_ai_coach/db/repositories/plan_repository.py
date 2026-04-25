"""Repository for Plan entities."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import Plan
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository


class PlanRepository(TrainingBaseRepository[Plan]):
    """Persist and retrieve Notion-backed Plan entities."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with an active SQLAlchemy session."""
        super().__init__(session, Plan)

    def get_active_for_datetime(self, now: datetime) -> Plan | None:
        """Return the active plan for *now* when a date window is available."""
        stmt = (
            select(Plan)
            .where(
                and_(
                    or_(Plan.start_date_start.is_not(None), Plan.end_date_start.is_not(None)),
                    or_(Plan.start_date_start.is_(None), Plan.start_date_start <= now),
                    or_(Plan.end_date_start.is_(None), Plan.end_date_start >= now),
                )
            )
            .order_by(Plan.start_date_start.is_(None), Plan.start_date_start.desc(), Plan.id.desc())
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def get_latest(self) -> Plan | None:
        """Return the latest plan by start date, falling back to primary key ordering."""
        stmt = (
            select(Plan)
            .order_by(Plan.start_date_start.is_(None), Plan.start_date_start.desc(), Plan.id.desc())
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none()
