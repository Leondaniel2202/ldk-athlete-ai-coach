"""Repository for Phase entity persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.phase import map_phase
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_phase import NotionPhase
from ldk_athlete_ai_coach.db.models.sport_manager import Phase


class PhaseRepository:
    """Handles database read and write operations for :class:`Phase` entities.

    All write operations are accumulated in the given session; callers are
    responsible for committing or flushing the session at the appropriate
    transaction boundary.

    Args:
        session: Active SQLAlchemy session bound to the target database.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_notion_id(self, notion_id: str) -> Phase | None:
        """Return the :class:`Phase` row with the given Notion page ID, or ``None``.

        Args:
            notion_id: Notion page ID to look up (``notion_page_id`` column).

        Returns:
            The matching :class:`Phase` instance, or ``None`` if not found.
        """
        return self._session.execute(
            select(Phase).where(Phase.notion_page_id == notion_id)
        ).scalar_one_or_none()

    def upsert(
        self,
        schema: NotionPhase,
        *,
        plan_id: int | None = None,
        nutrition_guideline_id: int | None = None,
    ) -> Phase:
        """Insert or update a :class:`Phase` row from a validated Notion schema.

        Looks up an existing row by ``notion_page_id``.  If found, the existing
        entity is updated in place using the mapper; otherwise a new entity is
        created and added to the session.

        Args:
            schema: Validated :class:`NotionPhase` Pydantic model.
            plan_id: Resolved local primary key of the related :class:`Plan` row.
                Pass ``None`` when the relation is not in scope.
            nutrition_guideline_id: Resolved local primary key of the related
                :class:`NutritionGuideline` row.  Pass ``None`` when the relation
                is not in scope.

        Returns:
            The inserted or updated :class:`Phase` entity (not yet committed).
        """
        existing = self.get_by_notion_id(schema.notion_id)
        entity = map_phase(
            schema,
            entity=existing,
            plan_id=plan_id,
            nutrition_guideline_id=nutrition_guideline_id,
        )
        if existing is None:
            self._session.add(entity)
        return entity
