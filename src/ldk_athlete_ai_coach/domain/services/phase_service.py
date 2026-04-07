"""Service layer for Phase domain operations."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.sport_manager import Phase, Workout
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository


class PhaseService:
    """Provide business-logic operations for :class:`Phase` entities.

    Attributes:
        _repo: Underlying :class:`PhaseRepository` instance.
    """

    def __init__(self, session: Session) -> None:
        """Initialise the service with an active database session.

        Args:
            session: Active SQLAlchemy session.
        """
        self._repo = PhaseRepository(session)

    def get_phase(self, phase_id: int) -> Phase | None:
        """Return the phase with the given ID, or ``None``.

        Args:
            phase_id: Primary key of the phase.

        Returns:
            :class:`Phase` instance, or ``None`` if not found.
        """
        return self._repo.get_by_id(phase_id)

    def get_phase_workouts(self, phase_id: int) -> list[Workout]:
        """Return all workouts belonging to the given phase.

        Args:
            phase_id: Primary key of the phase.

        Returns:
            List of :class:`Workout` instances ordered as stored.
        """
        return self._repo.get_workouts(phase_id)
