"""Repository for Plan entities."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.plan import map_plan
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_plan import NotionPlan
from ldk_athlete_ai_coach.db.models.sport_manager import Plan
from ldk_athlete_ai_coach.db.repositories.sport_manager_base_repository import (
    SportManagerBaseRepository,
)


class PlanRepository(SportManagerBaseRepository[Plan]):
    """Persist and retrieve Notion-backed Plan entities."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Plan)

    def upsert(self, schema: NotionPlan) -> Plan:
        """Insert or update a Plan row from a validated Notion schema."""

        existing = self.get_by_notion_id(schema.notion_id)
        entity = map_plan(schema, existing)
        if existing is None:
            self.add(entity)
        return entity
