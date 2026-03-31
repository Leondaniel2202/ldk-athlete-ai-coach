"""Repository for persisting Notion tracked-session schemas."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.session import map_session
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_session import NotionSession
from ldk_athlete_ai_coach.db.models.sport_manager import TrackedSession, Workout
from ldk_athlete_ai_coach.db.repositories.sport_manager_base_repository import (
    SportManagerBaseRepository,
)


class SessionRepository(SportManagerBaseRepository[TrackedSession]):
    """Persist extracted tracked-session schemas and resolve workout links."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, TrackedSession)
        self._workout_repository = SportManagerBaseRepository[Workout](session, Workout)

    def upsert(
        self,
        schema: NotionSession,
        *,
        workout_id: int | None = None,
    ) -> TrackedSession:
        """Insert or update a tracked-session row from a validated Notion schema."""
        existing = self.get_by_notion_id(schema.notion_id)
        resolved_workout_id = workout_id
        if resolved_workout_id is None and schema.workout_notion_id is not None:
            workout = self._workout_repository.get_by_notion_id(schema.workout_notion_id)
            resolved_workout_id = workout.id if workout is not None else None

        entity = map_session(schema, existing, workout_id=resolved_workout_id)
        if existing is None:
            self.add(entity)
        return entity