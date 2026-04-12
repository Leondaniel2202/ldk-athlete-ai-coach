"""Repository for TrackedSession entities."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import TrackedSession
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository


class SessionRepository(TrainingBaseRepository[TrackedSession]):
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

    def get_for_workout_ids(self, workout_ids: list[int]) -> list[TrackedSession]:
        """Return sessions linked to the given workout IDs."""
        if not workout_ids:
            return []
        stmt = (
            select(TrackedSession)
            .where(TrackedSession.workout_id.in_(workout_ids))
            .order_by(
                TrackedSession.workout_id.asc(),
                TrackedSession.start_start.desc(),
                TrackedSession.id.desc(),
            )
        )
        return list(self._session.execute(stmt).scalars().all())

    def get_recent_unlinked(self, since: datetime, now: datetime) -> list[TrackedSession]:
        """Return recent sessions that are not linked to any workout."""
        stmt = (
            select(TrackedSession)
            .where(
                TrackedSession.workout_id.is_(None),
                TrackedSession.start_start.is_not(None),
                TrackedSession.start_start >= since,
                TrackedSession.start_start <= now,
            )
            .order_by(TrackedSession.start_start.desc(), TrackedSession.id.desc())
        )
        return list(self._session.execute(stmt).scalars().all())
