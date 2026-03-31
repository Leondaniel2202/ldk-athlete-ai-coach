"""Repository for persisting Notion phase schemas."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.phase import map_phase
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_phase import NotionPhase
from ldk_athlete_ai_coach.db.models.sport_manager import Phase
from ldk_athlete_ai_coach.db.repositories.sport_manager_base_repository import (
    SportManagerBaseRepository,
)


class PhaseRepository(SportManagerBaseRepository[Phase]):
    """Persist extracted phase schemas into Phase rows."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Phase)

    def upsert(
        self,
        schema: NotionPhase,
        *,
        plan_id: int | None = None,
        nutrition_guideline_id: int | None = None,
    ) -> Phase:
        """Insert or update a phase row from a validated Notion schema."""
        existing = self.get_by_notion_id(schema.notion_id)
        entity = map_phase(
            schema,
            existing,
            plan_id=plan_id,
            nutrition_guideline_id=nutrition_guideline_id,
        )
        if existing is None:
            self.add(entity)
        return entity