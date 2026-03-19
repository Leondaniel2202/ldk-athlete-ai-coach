"""Repository for TrackedSession entity persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.session import map_session
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_session import NotionSession
from ldk_athlete_ai_coach.db.models.sport_manager import TrackedSession


class SessionRepository:
    """Handles database read and write operations for :class:`TrackedSession` entities.

    All write operations are accumulated in the given session; callers are
    responsible for committing or flushing the session at the appropriate
    transaction boundary.

    Args:
        session: Active SQLAlchemy session bound to the target database.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_notion_id(self, notion_id: str) -> TrackedSession | None:
        """Return the :class:`TrackedSession` row with the given Notion page ID, or ``None``.

        Args:
            notion_id: Notion page ID to look up (``notion_page_id`` column).

        Returns:
            The matching :class:`TrackedSession` instance, or ``None`` if not found.
        """
        return self._session.execute(
            select(TrackedSession).where(TrackedSession.notion_page_id == notion_id)
        ).scalar_one_or_none()

    def upsert(
        self,
        schema: NotionSession,
        *,
        workout_id: int | None = None,
    ) -> TrackedSession:
        """Insert or update a :class:`TrackedSession` row from a validated Notion schema.

        Looks up an existing row by ``notion_page_id``.  If found, the existing
        entity is updated in place using the mapper; otherwise a new entity is
        created and added to the session.

        Args:
            schema: Validated :class:`NotionSession` Pydantic model.
            workout_id: Resolved local primary key of the related :class:`Workout` row.
                Pass ``None`` when the relation is not yet resolved.

        Returns:
            The inserted or updated :class:`TrackedSession` entity (not yet committed).
        """
        existing = self.get_by_notion_id(schema.notion_id)
        entity = map_session(schema, entity=existing, workout_id=workout_id)
        if existing is None:
            self._session.add(entity)
        return entity
