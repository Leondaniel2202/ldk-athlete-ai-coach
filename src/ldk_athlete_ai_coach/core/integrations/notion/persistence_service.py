"""Thin orchestration layer for persisting extracted Notion schemas."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_phase import NotionPhase
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_session import NotionSession
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_weekly_feedback import (
    NotionWeeklyFeedback,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout
from ldk_athlete_ai_coach.db.models.sport_manager import Feedback, Phase, TrackedSession, Workout
from ldk_athlete_ai_coach.db.repositories.feedback_repository import FeedbackRepository
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository


class NotionPersistenceService:
    """Persist extracted Notion schemas in dependency order using repositories."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._phase_repository = PhaseRepository(session)
        self._workout_repository = WorkoutRepository(session)
        self._session_repository = SessionRepository(session)
        self._feedback_repository = FeedbackRepository(session)

    def persist_phases(self, phase_schemas: list[NotionPhase]) -> list[Phase]:
        """Persist phase schemas and flush generated primary keys."""
        entities = [self._phase_repository.upsert(schema) for schema in phase_schemas]
        self._session.flush()
        return entities

    def persist_workouts(self, workout_schemas: list[NotionWorkout]) -> list[Workout]:
        """Persist workout schemas, resolving any parent phase references."""
        entities = [self._workout_repository.upsert(schema) for schema in workout_schemas]
        self._session.flush()
        return entities

    def persist_sessions(self, session_schemas: list[NotionSession]) -> list[TrackedSession]:
        """Persist tracked-session schemas, resolving any parent workout references."""
        entities = [self._session_repository.upsert(schema) for schema in session_schemas]
        self._session.flush()
        return entities

    def persist_feedback(self, feedback_schemas: list[NotionWeeklyFeedback]) -> list[Feedback]:
        """Persist feedback schemas, resolving any parent phase references."""
        entities = [self._feedback_repository.upsert(schema) for schema in feedback_schemas]
        self._session.flush()
        return entities

    def persist_all(
        self,
        *,
        phase_schemas: list[NotionPhase],
        workout_schemas: list[NotionWorkout],
        session_schemas: list[NotionSession],
        feedback_schemas: list[NotionWeeklyFeedback],
    ) -> None:
        """Persist all extracted schema types in dependency order."""
        self.persist_phases(phase_schemas)
        self.persist_workouts(workout_schemas)
        self.persist_sessions(session_schemas)
        self.persist_feedback(feedback_schemas)