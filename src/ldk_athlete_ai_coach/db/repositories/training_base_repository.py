"""Generic repository helpers for training SQLAlchemy entities."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import TrainingEntityMixin


class TrainingBaseRepository[TEntity: TrainingEntityMixin]:
    """Provide shared database operations for training entities.

    Keep this small: only truly cross-entity persistence helpers belong here.
    """

    def __init__(self, session: Session, entity_cls: type[TEntity]) -> None:
        self._session = session
        self._entity_cls = entity_cls

    def get_by_id(self, entity_id: int) -> TEntity | None:
        return self._session.get(self._entity_cls, entity_id)

    def get_by_source_page_id(self, source_page_id: str) -> TEntity | None:
        """Return the entity with the given source page ID, or ``None``.

        Today this is backed by the `notion_page_id` column.
        """
        return self._session.execute(
            select(self._entity_cls).where(self._entity_cls.notion_page_id == source_page_id)
        ).scalar_one_or_none()

    def add(self, entity: TEntity) -> TEntity:
        self._session.add(entity)
        return entity

