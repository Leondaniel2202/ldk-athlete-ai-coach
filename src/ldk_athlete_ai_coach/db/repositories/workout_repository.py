"""Repository for persisting Notion workout schemas."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.workout import map_workout
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout
from ldk_athlete_ai_coach.db.models.sport_manager import Phase, Workout
from ldk_athlete_ai_coach.db.repositories.sport_manager_base_repository import (
    SportManagerBaseRepository,
)


class WorkoutRepository(SportManagerBaseRepository[Workout]):
    """Persist extracted workout schemas and resolve parent phase links."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Workout)
        self._phase_repository = SportManagerBaseRepository[Phase](session, Phase)

    def upsert(
        self,
        schema: NotionWorkout,
        *,
        phase_id: int | None = None,
    ) -> Workout:
        """Insert or update a workout row from a validated Notion schema."""
        existing = self.get_by_notion_id(schema.notion_id)
        resolved_phase_id = phase_id
        if resolved_phase_id is None and schema.phase_notion_id is not None:
            phase = self._phase_repository.get_by_notion_id(schema.phase_notion_id)
            resolved_phase_id = phase.id if phase is not None else None

        entity = map_workout(schema, existing, phase_id=resolved_phase_id)
        if existing is None:
            self.add(entity)
        return entity