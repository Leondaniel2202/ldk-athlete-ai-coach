"""Service layer for TrackedSession domain operations."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.sport_manager import TrackedSession
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository


class SessionService:
    """Provide business-logic operations for :class:`TrackedSession` entities.

    Attributes:
        _repo: Underlying :class:`SessionRepository` instance.
    """

    def __init__(self, session: Session) -> None:
        """Initialise the service with an active database session.

        Args:
            session: Active SQLAlchemy session.
        """
        self._repo = SessionRepository(session)

    def get_session(self, session_id: int) -> TrackedSession | None:
        """Return the tracked session with the given ID, or ``None``.

        Args:
            session_id: Primary key of the tracked session.

        Returns:
            :class:`TrackedSession` instance, or ``None`` if not found.
        """
        return self._repo.get_by_id(session_id)

    def get_recent_sessions(self, days: int = 14) -> list[TrackedSession]:
        """Return all tracked sessions from the last *days* days.

        Args:
            days: Look-back window in days (default: 14).

        Returns:
            List of :class:`TrackedSession` instances, newest first.
        """
        return self._repo.get_recent(days)
