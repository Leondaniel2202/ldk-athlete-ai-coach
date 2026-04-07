"""Repository for TrackedSession entities."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.sport_manager import TrackedSession
from ldk_athlete_ai_coach.db.repositories.sport_manager_base_repository import (
    SportManagerBaseRepository,
)


class SessionRepository(SportManagerBaseRepository[TrackedSession]):
    """Persistence layer for :class:`TrackedSession` entities."""

    def __init__(self, session: Session) -> None:
        """Initialise with an active database session."""
        super().__init__(session, TrackedSession)

    def get_recent(self, days: int) -> list[TrackedSession]:
        """Return sessions whose start date falls within the last *days* days.

        Args:
            days: Number of days to look back from now (inclusive).

        Returns:
            List of :class:`TrackedSession` rows ordered by start date descending.
        """
        cutoff = datetime.now(tz=UTC) - timedelta(days=days)
        stmt = (
            select(TrackedSession)
            .where(TrackedSession.start_start >= cutoff)
            .order_by(TrackedSession.start_start.desc())
        )
        return list(self._session.execute(stmt).scalars().all())
