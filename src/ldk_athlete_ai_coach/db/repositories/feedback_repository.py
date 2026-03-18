"""Repository for Feedback entity persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.feedback import map_feedback
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_weekly_feedback import (
    NotionWeeklyFeedback,
)
from ldk_athlete_ai_coach.db.models.sport_manager import Feedback


class FeedbackRepository:
    """Handles database read and write operations for :class:`Feedback` entities.

    All write operations are accumulated in the given session; callers are
    responsible for committing or flushing the session at the appropriate
    transaction boundary.

    Args:
        session: Active SQLAlchemy session bound to the target database.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_notion_id(self, notion_id: str) -> Feedback | None:
        """Return the :class:`Feedback` row with the given Notion page ID, or ``None``.

        Args:
            notion_id: Notion page ID to look up (``notion_page_id`` column).

        Returns:
            The matching :class:`Feedback` instance, or ``None`` if not found.
        """
        return self._session.execute(
            select(Feedback).where(Feedback.notion_page_id == notion_id)
        ).scalar_one_or_none()

    def upsert(
        self,
        schema: NotionWeeklyFeedback,
        *,
        phase_id: int | None = None,
    ) -> Feedback:
        """Insert or update a :class:`Feedback` row from a validated Notion schema.

        Looks up an existing row by ``notion_page_id``.  If found, the existing
        entity is updated in place using the mapper; otherwise a new entity is
        created and added to the session.

        Args:
            schema: Validated :class:`NotionWeeklyFeedback` Pydantic model.
            phase_id: Resolved local primary key of the related :class:`Phase` row.
                Pass ``None`` when the relation is not yet resolved.

        Returns:
            The inserted or updated :class:`Feedback` entity (not yet committed).
        """
        existing = self.get_by_notion_id(schema.notion_id)
        entity = map_feedback(schema, entity=existing, phase_id=phase_id)
        if existing is None:
            self._session.add(entity)
        return entity
