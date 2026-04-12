"""Repository for Plan entities."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.plan import map_plan
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_plan import NotionPlan
from ldk_athlete_ai_coach.db.models.training import Phase, Plan
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository


class PlanRepository(TrainingBaseRepository[Plan]):
    """Persist and retrieve Notion-backed Plan entities."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Plan)

    def get_phases(self, plan_id: int) -> list[Phase]:
        """Return all phases that belong to the given plan.

        Args:
            plan_id: Primary key of the parent plan.

        Returns:
            Ordered list of :class:`Phase` rows.
        """
        plan = self._session.get(Plan, plan_id)
        if plan is None:
            return []
        return list(plan.phases)

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
