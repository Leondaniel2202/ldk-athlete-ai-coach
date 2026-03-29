"""Generic repository helpers for Notion-backed SQLAlchemy entities."""

from __future__ import annotations

from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.entitys.sport_manager import (
    NutritionGuideline,
    Phase,
    TrackedSession,
    WeeklyFeedback,
    Workout,
)

TEntity = TypeVar(
    "TEntity",
    Phase,
    Workout,
    NutritionGuideline,
    TrackedSession,
    WeeklyFeedback,
)


class SportManagerBaseRepository[TEntity]:
    """Provide shared database operations for Notion-backed entities.

    This base repository is intentionally small. It only contains logic that is
    truly common across all Notion-synced SQLAlchemy entitys.

    All write operations are accumulated in the provided SQLAlchemy session.
    Callers are responsible for flushing or committing at the appropriate
    transaction boundary.
    """

    def __init__(self, session: Session, entity_cls: type[TEntity]) -> None:
        """Initialize the repository.

        Args:
            session: Active SQLAlchemy session.
            entity_cls: SQLAlchemy entity class handled by this repository.
        """
        self._session = session
        self._entity_cls = entity_cls

    def get_by_notion_id(self, notion_id: str) -> TEntity | None:
        """Return the entity with the given Notion page ID, or ``None``.

        Args:
            notion_id: Notion page ID stored in the ``notion_page_id`` column.

        Returns:
            The matching SQLAlchemy entity, or ``None`` if not found.
        """
        return self._session.execute(
            select(self._entity_cls).where(self._entity_cls.notion_page_id == notion_id)
        ).scalar_one_or_none()

    def add(self, entity: TEntity) -> TEntity:
        """Add a new entity to the current session.

        Args:
            entity: SQLAlchemy entity instance to add.

        Returns:
            The same entity instance.
        """
        self._session.add(entity)
        return entity