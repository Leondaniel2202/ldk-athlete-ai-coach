"""Repository for persisting Notion feedback schemas."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.feedback import map_feedback
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_weekly_feedback import (
    NotionWeeklyFeedback,
)
from ldk_athlete_ai_coach.db.models.sport_manager import Phase, WeeklyFeedback
from ldk_athlete_ai_coach.db.repositories.sport_manager_base_repository import (
    SportManagerBaseRepository,
)


class FeedbackRepository(SportManagerBaseRepository[WeeklyFeedback]):
    """Persist extracted feedback schemas and resolve parent phase links."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, WeeklyFeedback)
        self._phase_repository = SportManagerBaseRepository[Phase](session, Phase)

    def upsert(
        self,
        schema: NotionWeeklyFeedback,
        *,
        phase_id: int | None = None,
    ) -> WeeklyFeedback:
        """Insert or update a feedback row from a validated Notion schema."""
        existing = self.get_by_notion_id(schema.notion_id)
        resolved_phase_id = phase_id
        if resolved_phase_id is None and schema.phase_notion_id is not None:
            phase = self._phase_repository.get_by_notion_id(schema.phase_notion_id)
            resolved_phase_id = phase.id if phase is not None else None

        entity = map_feedback(schema, existing, phase_id=resolved_phase_id)
        if existing is None:
            self.add(entity)
        return entity