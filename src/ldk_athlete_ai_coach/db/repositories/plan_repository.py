"""Repository for Plan entities."""

from __future__ import annotations

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
