"""Notion persistence service.

This module is responsible for safely writing Notion-derived data to
PostgreSQL.  It receives validated Pydantic schemas from the sync boundary,
resolves foreign-key relationships between entities, and delegates the actual
insert/update logic to the per-entity repositories.

All write operations within a single :meth:`~NotionPersistenceService.persist_all`
call are wrapped in one transaction; each targeted ``persist_*`` helper flushes
the session so that auto-generated primary keys are available for subsequent
FK resolution steps.

Typical usage (called from the sync service or an orchestration layer)::

    from sqlalchemy.orm import Session
    from ldk_athlete_ai_coach.core.integrations.notion.persistence_service import (
        NotionPersistenceService,
    )

    def run_sync(session: Session, phase_schemas, workout_schemas, ...) -> None:
        svc = NotionPersistenceService(session)
        svc.persist_all(phase_schemas, workout_schemas, session_schemas, feedback_schemas)
"""

from __future__ import annotations

import logging

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

logger = logging.getLogger(__name__)


class NotionPersistenceService:
    """Orchestrates idempotent persistence of Notion-derived entities.

    Entities are written to the database using an upsert strategy: existing
    rows (identified by ``notion_page_id``) are updated in place; new rows are
    inserted.  Notion is treated as the source of truth—no conflict resolution
    or change-detection is applied.

    Foreign-key relationships are resolved by looking up already-persisted
    parent rows within the same session before writing dependent entities.
    Entities must therefore be persisted in dependency order:

    1. **Phase** – no in-scope upstream dependencies.
    2. **Workout** – depends on Phase.
    3. **TrackedSession** – depends on Workout.
    4. **Feedback** – depends on Phase.

    Args:
        session: Active SQLAlchemy session.  Transaction boundaries (commit /
            rollback) are the caller's responsibility unless
            :meth:`persist_all` is used, which commits automatically.
    """

    def __init__(self, session: Session) -> None:
        self._session = session
        self._phase_repo = PhaseRepository(session)
        self._workout_repo = WorkoutRepository(session)
        self._session_repo = SessionRepository(session)
        self._feedback_repo = FeedbackRepository(session)

    # ------------------------------------------------------------------
    # Per-entity persist helpers
    # ------------------------------------------------------------------

    def persist_phases(self, schemas: list[NotionPhase]) -> list[Phase]:
        """Upsert all Phase schemas and flush the session.

        Phase has no in-scope FK dependencies; ``plan_id`` and
        ``nutrition_guideline_id`` are resolved against any already-persisted
        rows but default to ``None`` when the parent does not exist.

        Args:
            schemas: Validated :class:`NotionPhase` schemas to persist.

        Returns:
            List of persisted :class:`Phase` entities in input order.
        """
        entities: list[Phase] = []
        for schema in schemas:
            entity = self._phase_repo.upsert(schema)
            entities.append(entity)
            logger.debug(
                "Upserted Phase notion_id=%s",
                schema.notion_id,
            )
        self._session.flush()
        return entities

    def persist_workouts(self, schemas: list[NotionWorkout]) -> list[Workout]:
        """Upsert all Workout schemas and flush the session.

        For each schema, the related :class:`Phase` is looked up by
        ``phase_notion_id`` so that the local ``phase_id`` FK can be resolved.

        Args:
            schemas: Validated :class:`NotionWorkout` schemas to persist.

        Returns:
            List of persisted :class:`Workout` entities in input order.
        """
        entities: list[Workout] = []
        for schema in schemas:
            phase_id: int | None = None
            if schema.phase_notion_id:
                phase = self._phase_repo.get_by_notion_id(schema.phase_notion_id)
                if phase is not None:
                    phase_id = phase.id
            entity = self._workout_repo.upsert(schema, phase_id=phase_id)
            entities.append(entity)
            logger.debug(
                "Upserted Workout notion_id=%s phase_id=%s",
                schema.notion_id,
                phase_id,
            )
        self._session.flush()
        return entities

    def persist_sessions(self, schemas: list[NotionSession]) -> list[TrackedSession]:
        """Upsert all TrackedSession schemas and flush the session.

        For each schema, the related :class:`Workout` is looked up by
        ``workout_notion_id`` so that the local ``workout_id`` FK can be
        resolved.

        Args:
            schemas: Validated :class:`NotionSession` schemas to persist.

        Returns:
            List of persisted :class:`TrackedSession` entities in input order.
        """
        entities: list[TrackedSession] = []
        for schema in schemas:
            workout_id: int | None = None
            if schema.workout_notion_id:
                workout = self._workout_repo.get_by_notion_id(schema.workout_notion_id)
                if workout is not None:
                    workout_id = workout.id
            entity = self._session_repo.upsert(schema, workout_id=workout_id)
            entities.append(entity)
            logger.debug(
                "Upserted TrackedSession notion_id=%s workout_id=%s",
                schema.notion_id,
                workout_id,
            )
        self._session.flush()
        return entities

    def persist_feedback(self, schemas: list[NotionWeeklyFeedback]) -> list[Feedback]:
        """Upsert all Feedback schemas and flush the session.

        For each schema, the related :class:`Phase` is looked up by
        ``phase_notion_id`` so that the local ``phase_id`` FK can be resolved.

        Args:
            schemas: Validated :class:`NotionWeeklyFeedback` schemas to persist.

        Returns:
            List of persisted :class:`Feedback` entities in input order.
        """
        entities: list[Feedback] = []
        for schema in schemas:
            phase_id: int | None = None
            if schema.phase_notion_id:
                phase = self._phase_repo.get_by_notion_id(schema.phase_notion_id)
                if phase is not None:
                    phase_id = phase.id
            entity = self._feedback_repo.upsert(schema, phase_id=phase_id)
            entities.append(entity)
            logger.debug(
                "Upserted Feedback notion_id=%s phase_id=%s",
                schema.notion_id,
                phase_id,
            )
        self._session.flush()
        return entities

    # ------------------------------------------------------------------
    # Aggregate persist (full sync transaction)
    # ------------------------------------------------------------------

    def persist_all(
        self,
        phase_schemas: list[NotionPhase],
        workout_schemas: list[NotionWorkout],
        session_schemas: list[NotionSession],
        feedback_schemas: list[NotionWeeklyFeedback],
    ) -> None:
        """Persist all entity types in dependency order and commit the transaction.

        Entities are persisted in the following order so that FK resolution
        succeeds within a single transaction:

        1. Phase
        2. Workout (FK → Phase)
        3. TrackedSession (FK → Workout)
        4. Feedback (FK → Phase)

        The session is committed on success.  On error the exception is
        propagated to the caller and the session is left in an undetermined
        state; callers should perform a rollback as appropriate.

        Args:
            phase_schemas: Validated :class:`NotionPhase` schemas.
            workout_schemas: Validated :class:`NotionWorkout` schemas.
            session_schemas: Validated :class:`NotionSession` schemas.
            feedback_schemas: Validated :class:`NotionWeeklyFeedback` schemas.
        """
        logger.info(
            "Starting persistence run "
            "phases=%d workouts=%d sessions=%d feedback=%d",
            len(phase_schemas),
            len(workout_schemas),
            len(session_schemas),
            len(feedback_schemas),
        )
        self.persist_phases(phase_schemas)
        self.persist_workouts(workout_schemas)
        self.persist_sessions(session_schemas)
        self.persist_feedback(feedback_schemas)
        self._session.commit()
        logger.info("Persistence run committed successfully")
