"""Repository for Phase entities."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.sport_manager import Phase, Workout
from ldk_athlete_ai_coach.db.repositories.sport_manager_base_repository import (
    SportManagerBaseRepository,
)


class PhaseRepository(SportManagerBaseRepository[Phase]):
    """Persistence layer for :class:`Phase` entities."""

    def __init__(self, session: Session) -> None:
        """Initialise with an active database session."""
        super().__init__(session, Phase)

    def get_workouts(self, phase_id: int) -> list[Workout]:
        """Return all workouts that belong to the given phase.

        Args:
            phase_id: Primary key of the parent phase.

        Returns:
            Ordered list of :class:`Workout` rows.
        """
        phase = self._session.get(Phase, phase_id)
        if phase is None:
            return []
        return list(phase.workouts)
