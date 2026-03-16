"""Notion sync service – orchestrates fetch → transform → upsert.

The service fetches every page from each configured Notion database, transforms
it into domain model kwargs, and upserts the result into the local PostgreSQL
database using SQLAlchemy.

Sync order respects foreign-key dependencies:
  1. Plans                    (no FK to other synced tables)
  2. NutritionGuidelines      (no FK)
  3. TrainingLoads             (no FK)
  4. Phases                   (FK → Plans, NutritionGuidelines)
  5. Workouts                 (FK → Phases)
  6. Events                   (FK → Plans, Workouts)
  7. TrackedSessions           (FK → Workouts)
  8. Feedback                 (FK → Phases)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.sport_manager import (
    Event,
    Feedback,
    NutritionGuideline,
    Phase,
    Plan,
    TrackedSession,
    TrainingLoad,
    Workout,
)
from ldk_athlete_ai_coach.notion_sync import transformers

if TYPE_CHECKING:
    from ldk_athlete_ai_coach.notion_sync.client import NotionClient

logger = logging.getLogger(__name__)

# Type alias for a notion_page_id → local primary key mapping
_IdMap = dict[str, int]


class NotionSyncService:
    """Fetches Notion pages and upserts them into the local database.

    Args:
        client: A :class:`~ldk_athlete_ai_coach.notion_sync.client.NotionClient`
            instance used to query the Notion API.
        session: Active SQLAlchemy :class:`~sqlalchemy.orm.Session`.
        db_events: Notion database ID for the Events database (optional).
        db_plans: Notion database ID for the Plans database (optional).
        db_phases: Notion database ID for the Phases database (optional).
        db_workouts: Notion database ID for the Workouts database (optional).
        db_tracked_sessions: Notion database ID for Tracked Sessions (optional).
        db_nutrition_guidelines: Notion database ID for Nutrition Guidelines (optional).
        db_training_loads: Notion database ID for Training Loads (optional).
        db_feedback: Notion database ID for the Feedback database (optional).
    """

    def __init__(
        self,
        client: NotionClient,
        session: Session,
        *,
        db_events: str | None = None,
        db_plans: str | None = None,
        db_phases: str | None = None,
        db_workouts: str | None = None,
        db_tracked_sessions: str | None = None,
        db_nutrition_guidelines: str | None = None,
        db_training_loads: str | None = None,
        db_feedback: str | None = None,
    ) -> None:
        self._client = client
        self._session = session
        self._db_events = db_events
        self._db_plans = db_plans
        self._db_phases = db_phases
        self._db_workouts = db_workouts
        self._db_tracked_sessions = db_tracked_sessions
        self._db_nutrition_guidelines = db_nutrition_guidelines
        self._db_training_loads = db_training_loads
        self._db_feedback = db_feedback

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sync_all(self) -> None:
        """Run a full sync for every configured Notion database.

        Databases without a configured ID are silently skipped.  The session is
        committed once after all entities have been processed.
        """
        plan_ids = self.sync_plans()
        nutrition_ids = self.sync_nutrition_guidelines()
        self.sync_training_loads()
        phase_ids = self.sync_phases(plan_ids=plan_ids, nutrition_ids=nutrition_ids)
        workout_ids = self.sync_workouts(phase_ids=phase_ids)
        self.sync_events(plan_ids=plan_ids, workout_ids=workout_ids)
        self.sync_tracked_sessions(workout_ids=workout_ids)
        self.sync_feedback(phase_ids=phase_ids)
        self._session.commit()

    def sync_plans(self) -> _IdMap:
        """Fetch and upsert all Plans.

        Returns:
            Mapping of ``notion_page_id`` → local ``Plan.id``.
        """
        return self._sync_simple(Plan, self._db_plans, transformers.transform_plan)

    def sync_nutrition_guidelines(self) -> _IdMap:
        """Fetch and upsert all Nutrition Guidelines.

        Returns:
            Mapping of ``notion_page_id`` → local ``NutritionGuideline.id``.
        """
        return self._sync_simple(
            NutritionGuideline,
            self._db_nutrition_guidelines,
            transformers.transform_nutrition_guideline,
        )

    def sync_training_loads(self) -> _IdMap:
        """Fetch and upsert all Training Loads.

        Returns:
            Mapping of ``notion_page_id`` → local ``TrainingLoad.id``.
        """
        return self._sync_simple(
            TrainingLoad,
            self._db_training_loads,
            transformers.transform_training_load,
        )

    def sync_phases(
        self,
        *,
        plan_ids: _IdMap | None = None,
        nutrition_ids: _IdMap | None = None,
    ) -> _IdMap:
        """Fetch and upsert all Phases, resolving FK relations.

        Args:
            plan_ids: Mapping of Plan ``notion_page_id`` → local id.
            nutrition_ids: Mapping of NutritionGuideline ``notion_page_id`` → local id.

        Returns:
            Mapping of ``notion_page_id`` → local ``Phase.id``.
        """
        if not self._db_phases:
            return {}

        pages = self._client.query_database(self._db_phases)
        id_map: _IdMap = {}

        for page in pages:
            kwargs = transformers.transform_phase(page)
            plan_notion_id = kwargs.pop("plan_notion_id", None)
            nutrition_notion_id = kwargs.pop("nutrition_notion_id", None)

            if plan_ids and plan_notion_id:
                kwargs["plan_id"] = plan_ids.get(plan_notion_id.replace("-", ""))
            if nutrition_ids and nutrition_notion_id:
                kwargs["nutrition_guideline_id"] = nutrition_ids.get(
                    nutrition_notion_id.replace("-", "")
                )

            obj = self._upsert(Phase, kwargs)
            if obj.id is not None:
                id_map[obj.notion_page_id] = obj.id

        logger.info("Synced %d phases", len(id_map))
        return id_map

    def sync_workouts(self, *, phase_ids: _IdMap | None = None) -> _IdMap:
        """Fetch and upsert all Workouts, resolving FK relations.

        Args:
            phase_ids: Mapping of Phase ``notion_page_id`` → local id.

        Returns:
            Mapping of ``notion_page_id`` → local ``Workout.id``.
        """
        if not self._db_workouts:
            return {}

        pages = self._client.query_database(self._db_workouts)
        id_map: _IdMap = {}

        for page in pages:
            kwargs = transformers.transform_workout(page)
            phase_notion_id = kwargs.pop("phase_notion_id", None)

            if phase_ids and phase_notion_id:
                kwargs["phase_id"] = phase_ids.get(phase_notion_id.replace("-", ""))

            obj = self._upsert(Workout, kwargs)
            if obj.id is not None:
                id_map[obj.notion_page_id] = obj.id

        logger.info("Synced %d workouts", len(id_map))
        return id_map

    def sync_events(
        self,
        *,
        plan_ids: _IdMap | None = None,
        workout_ids: _IdMap | None = None,
    ) -> _IdMap:
        """Fetch and upsert all Events, resolving FK relations.

        Args:
            plan_ids: Mapping of Plan ``notion_page_id`` → local id.
            workout_ids: Mapping of Workout ``notion_page_id`` → local id.

        Returns:
            Mapping of ``notion_page_id`` → local ``Event.id``.
        """
        if not self._db_events:
            return {}

        pages = self._client.query_database(self._db_events)
        id_map: _IdMap = {}

        for page in pages:
            kwargs = transformers.transform_event(page)
            plan_notion_id = kwargs.pop("plan_notion_id", None)
            race_workout_notion_id = kwargs.pop("race_workout_notion_id", None)

            if plan_ids and plan_notion_id:
                kwargs["plan_id"] = plan_ids.get(plan_notion_id.replace("-", ""))
            if workout_ids and race_workout_notion_id:
                kwargs["race_workout_id"] = workout_ids.get(race_workout_notion_id.replace("-", ""))

            obj = self._upsert(Event, kwargs)
            if obj.id is not None:
                id_map[obj.notion_page_id] = obj.id

        logger.info("Synced %d events", len(id_map))
        return id_map

    def sync_tracked_sessions(self, *, workout_ids: _IdMap | None = None) -> _IdMap:
        """Fetch and upsert all Tracked Sessions, resolving FK relations.

        Args:
            workout_ids: Mapping of Workout ``notion_page_id`` → local id.

        Returns:
            Mapping of ``notion_page_id`` → local ``TrackedSession.id``.
        """
        if not self._db_tracked_sessions:
            return {}

        pages = self._client.query_database(self._db_tracked_sessions)
        id_map: _IdMap = {}

        for page in pages:
            kwargs = transformers.transform_tracked_session(page)
            workout_notion_id = kwargs.pop("workout_notion_id", None)

            if workout_ids and workout_notion_id:
                kwargs["workout_id"] = workout_ids.get(workout_notion_id.replace("-", ""))

            obj = self._upsert(TrackedSession, kwargs)
            if obj.id is not None:
                id_map[obj.notion_page_id] = obj.id

        logger.info("Synced %d tracked sessions", len(id_map))
        return id_map

    def sync_feedback(self, *, phase_ids: _IdMap | None = None) -> _IdMap:
        """Fetch and upsert all Feedback entries, resolving FK relations.

        Args:
            phase_ids: Mapping of Phase ``notion_page_id`` → local id.

        Returns:
            Mapping of ``notion_page_id`` → local ``Feedback.id``.
        """
        if not self._db_feedback:
            return {}

        pages = self._client.query_database(self._db_feedback)
        id_map: _IdMap = {}

        for page in pages:
            kwargs = transformers.transform_feedback(page)
            phase_notion_id = kwargs.pop("phase_notion_id", None)

            if phase_ids and phase_notion_id:
                kwargs["phase_id"] = phase_ids.get(phase_notion_id.replace("-", ""))

            obj = self._upsert(Feedback, kwargs)
            if obj.id is not None:
                id_map[obj.notion_page_id] = obj.id

        logger.info("Synced %d feedback entries", len(id_map))
        return id_map

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sync_simple(
        self,
        model_cls: type,
        database_id: str | None,
        transform_fn: Any,
    ) -> _IdMap:
        """Fetch all pages from *database_id*, transform them, and upsert.

        Args:
            model_cls: The SQLAlchemy model class to upsert into.
            database_id: Notion database UUID to query; returns empty dict if ``None``.
            transform_fn: Callable that converts a raw Notion page dict to model kwargs.

        Returns:
            Mapping of ``notion_page_id`` → local primary key.
        """
        if not database_id:
            return {}

        pages = self._client.query_database(database_id)
        id_map: _IdMap = {}

        for page in pages:
            kwargs = transform_fn(page)
            obj = self._upsert(model_cls, kwargs)
            if obj.id is not None:
                id_map[obj.notion_page_id] = obj.id

        logger.info("Synced %d %s records", len(id_map), model_cls.__name__)
        return id_map

    def _upsert(self, model_cls: type, kwargs: dict) -> Any:
        """Insert a new row or update an existing one matched by ``notion_page_id``.

        Args:
            model_cls: SQLAlchemy model class.
            kwargs: Column values including ``notion_page_id``.

        Returns:
            The created or updated model instance (not yet committed).
        """
        notion_page_id: str = kwargs["notion_page_id"]
        obj = self._session.query(model_cls).filter_by(notion_page_id=notion_page_id).one_or_none()

        if obj is None:
            obj = model_cls(**kwargs)
            self._session.add(obj)
        else:
            for key, value in kwargs.items():
                setattr(obj, key, value)

        self._session.flush()
        return obj
