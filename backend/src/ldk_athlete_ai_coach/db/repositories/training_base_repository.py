"""Generic repository helpers for training SQLAlchemy entities."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import TrainingEntityMixin


class TrainingBaseRepository[TEntity: TrainingEntityMixin]:
    """Provide shared database operations for training entities.

    Keep this small: only truly cross-entity persistence helpers belong here.
    """

    def __init__(self, session: Session, entity_cls: type[TEntity]) -> None:
        """Initialize repository state for a given entity type.

        Args:
            session: Active SQLAlchemy session.
            entity_cls: SQLAlchemy model class handled by this repository.

        """
        self._session = session
        self._entity_cls = entity_cls

    def get_by_id(self, entity_id: int) -> TEntity | None:
        """Return one entity by primary key, or ``None`` when not found."""
        return self._session.get(self._entity_cls, entity_id)

    def add(self, entity: TEntity) -> TEntity:
        """Add an entity to the current session and return it."""
        self._session.add(entity)
        return entity
