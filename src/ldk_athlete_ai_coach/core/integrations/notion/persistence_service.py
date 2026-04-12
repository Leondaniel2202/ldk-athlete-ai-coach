"""Notion-aware persistence boundary for extracted schemas."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.mappers.event import map_event
from ldk_athlete_ai_coach.core.integrations.notion.mappers.feedback import map_feedback
from ldk_athlete_ai_coach.core.integrations.notion.mappers.nutrition import map_nutrition
from ldk_athlete_ai_coach.core.integrations.notion.mappers.phase import map_phase
from ldk_athlete_ai_coach.core.integrations.notion.mappers.plan import map_plan
from ldk_athlete_ai_coach.core.integrations.notion.mappers.session import map_session
from ldk_athlete_ai_coach.core.integrations.notion.mappers.workout import map_workout
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_event import NotionEvent
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_nutrition_guideline import (
    NotionNutritionGuideline,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_phase import NotionPhase
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_plan import NotionPlan
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_session import NotionSession
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_weekly_feedback import (
    NotionWeeklyFeedback,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout
from ldk_athlete_ai_coach.db.models.training import (
    Event,
    Feedback,
    NutritionGuideline,
    Phase,
    Plan,
    TrackedSession,
    TrainingEntityMixin,
    Workout,
)
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository


class NotionPersistenceService:
    """Persist extracted Notion schemas in dependency order using repositories."""

    def __init__(self, session: Session) -> None:
        """Initialize the persistence service and typed repositories.

        Args:
            session: Active SQLAlchemy session used for all repository operations.

        """
        self._session = session
        self._plan_repository = TrainingBaseRepository[Plan](session, Plan)
        self._nutrition_guideline_repository = TrainingBaseRepository[NutritionGuideline](
            session, NutritionGuideline
        )
        self._phase_repository = TrainingBaseRepository[Phase](session, Phase)
        self._workout_repository = TrainingBaseRepository[Workout](session, Workout)
        self._event_repository = TrainingBaseRepository[Event](session, Event)
        self._session_repository = TrainingBaseRepository[TrackedSession](session, TrackedSession)
        self._feedback_repository = TrainingBaseRepository[Feedback](session, Feedback)

    def persist_plans(self, plan_schemas: list[NotionPlan]) -> list[Plan]:
        """Map and persist plan schemas.

        Args:
            plan_schemas: Extracted Plan schemas from Notion.

        Returns:
            Persisted or updated Plan entities.

        """
        entities: list[Plan] = []
        for schema in plan_schemas:
            existing = self._plan_repository.get_by_source_page_id(schema.notion_id)
            entity = map_plan(schema, existing)
            entities.append(self._add_if_new(self._plan_repository, existing, entity))
        self._session.flush()
        return entities

    def persist_nutrition_guidelines(
        self,
        nutrition_schemas: list[NotionNutritionGuideline],
    ) -> list[NutritionGuideline]:
        """Map and persist nutrition-guideline schemas."""
        entities: list[NutritionGuideline] = []
        for schema in nutrition_schemas:
            existing = self._nutrition_guideline_repository.get_by_source_page_id(schema.notion_id)
            entity = map_nutrition(schema, existing)
            entities.append(self._add_if_new(self._nutrition_guideline_repository, existing, entity))
        self._session.flush()
        return entities

    def persist_phases(self, phase_schemas: list[NotionPhase]) -> list[Phase]:
        """Map and persist phase schemas.

        Args:
            phase_schemas: Extracted Phase schemas from Notion.

        Returns:
            Persisted or updated Phase entities.

        """
        entities: list[Phase] = []
        for schema in phase_schemas:
            existing = self._phase_repository.get_by_source_page_id(schema.notion_id)
            plan_id = self._resolve_plan_id(schema.plan_notion_id)
            nutrition_guideline_id = self._resolve_nutrition_guideline_id(
                schema.nutrition_guideline_notion_id
            )
            entity = map_phase(
                schema,
                existing,
                plan_id=plan_id,
                nutrition_guideline_id=nutrition_guideline_id,
            )
            entities.append(self._add_if_new(self._phase_repository, existing, entity))
        self._session.flush()
        return entities

    def persist_workouts(self, workout_schemas: list[NotionWorkout]) -> list[Workout]:
        """Map and persist workout schemas, resolving phase foreign keys.

        Args:
            workout_schemas: Extracted Workout schemas from Notion.

        Returns:
            Persisted or updated Workout entities.

        """
        entities: list[Workout] = []
        for schema in workout_schemas:
            existing = self._workout_repository.get_by_source_page_id(schema.notion_id)
            phase_id = self._resolve_phase_id(schema.phase_notion_id)
            entity = map_workout(schema, existing, phase_id=phase_id)
            entities.append(self._add_if_new(self._workout_repository, existing, entity))
        self._session.flush()
        return entities

    def persist_events(self, event_schemas: list[NotionEvent]) -> list[Event]:
        """Map and persist event schemas, resolving plan and workout foreign keys."""
        entities: list[Event] = []
        for schema in event_schemas:
            existing = self._event_repository.get_by_source_page_id(schema.notion_id)
            plan_id = self._resolve_plan_id(schema.plan_notion_id)
            race_workout_id = self._resolve_workout_id(schema.race_workout_notion_id)
            entity = map_event(
                schema,
                existing,
                plan_id=plan_id,
                race_workout_id=race_workout_id,
            )
            entities.append(self._add_if_new(self._event_repository, existing, entity))
        self._session.flush()
        return entities

    def persist_sessions(self, session_schemas: list[NotionSession]) -> list[TrackedSession]:
        """Map and persist tracked-session schemas, resolving workout foreign keys.

        Args:
            session_schemas: Extracted TrackedSession schemas from Notion.

        Returns:
            Persisted or updated TrackedSession entities.

        """
        entities: list[TrackedSession] = []
        for schema in session_schemas:
            existing = self._session_repository.get_by_source_page_id(schema.notion_id)
            workout_id = self._resolve_workout_id(schema.workout_notion_id)
            entity = map_session(schema, existing, workout_id=workout_id)
            entities.append(self._add_if_new(self._session_repository, existing, entity))
        self._session.flush()
        return entities

    def persist_feedback(self, feedback_schemas: list[NotionWeeklyFeedback]) -> list[Feedback]:
        """Map and persist feedback schemas, resolving phase foreign keys.

        Args:
            feedback_schemas: Extracted Feedback schemas from Notion.

        Returns:
            Persisted or updated Feedback entities.

        """
        entities: list[Feedback] = []
        for schema in feedback_schemas:
            existing = self._feedback_repository.get_by_source_page_id(schema.notion_id)
            phase_id = self._resolve_phase_id(schema.phase_notion_id)
            entity = map_feedback(schema, existing, phase_id=phase_id)
            entities.append(self._add_if_new(self._feedback_repository, existing, entity))
        self._session.flush()
        return entities

    def persist_all(
        self,
        *,
        plan_schemas: list[NotionPlan],
        nutrition_guideline_schemas: list[NotionNutritionGuideline],
        phase_schemas: list[NotionPhase],
        workout_schemas: list[NotionWorkout],
        event_schemas: list[NotionEvent],
        session_schemas: list[NotionSession],
        feedback_schemas: list[NotionWeeklyFeedback],
    ) -> None:
        """Persist all extracted schema types in dependency order.

        Args:
            plan_schemas: Extracted Plan schemas.
            nutrition_guideline_schemas: Extracted Nutrition Guideline schemas.
            phase_schemas: Extracted Phase schemas.
            workout_schemas: Extracted Workout schemas.
            event_schemas: Extracted Event schemas.
            session_schemas: Extracted TrackedSession schemas.
            feedback_schemas: Extracted Feedback schemas.

        """
        self.persist_plans(plan_schemas)
        self.persist_nutrition_guidelines(nutrition_guideline_schemas)
        self.persist_phases(phase_schemas)
        self.persist_workouts(workout_schemas)
        self.persist_events(event_schemas)
        self.persist_sessions(session_schemas)
        self.persist_feedback(feedback_schemas)

    def _resolve_plan_id(self, notion_id: str | None) -> int | None:
        """Resolve a plan Notion page ID to a local primary key.

        Args:
            notion_id: Notion page ID for a Plan, if present.

        Returns:
            Local Plan primary key, or ``None`` when unresolved.

        """
        if notion_id is None:
            return None
        plan = self._plan_repository.get_by_source_page_id(notion_id)
        return plan.id if plan is not None else None

    def _resolve_nutrition_guideline_id(self, notion_id: str | None) -> int | None:
        """Resolve a nutrition-guideline Notion page ID to a local primary key."""
        if notion_id is None:
            return None
        guideline = self._nutrition_guideline_repository.get_by_source_page_id(notion_id)
        return guideline.id if guideline is not None else None

    def _resolve_phase_id(self, notion_id: str | None) -> int | None:
        """Resolve a phase Notion page ID to a local primary key.

        Args:
            notion_id: Notion page ID for a Phase, if present.

        Returns:
            Local Phase primary key, or ``None`` when unresolved.

        """
        if notion_id is None:
            return None
        phase = self._phase_repository.get_by_source_page_id(notion_id)
        return phase.id if phase is not None else None

    def _resolve_workout_id(self, notion_id: str | None) -> int | None:
        """Resolve a workout Notion page ID to a local primary key.

        Args:
            notion_id: Notion page ID for a Workout, if present.

        Returns:
            Local Workout primary key, or ``None`` when unresolved.

        """
        if notion_id is None:
            return None
        workout = self._workout_repository.get_by_source_page_id(notion_id)
        return workout.id if workout is not None else None

    @staticmethod
    def _add_if_new[TEntity: TrainingEntityMixin](
        repository: TrainingBaseRepository[TEntity],
        existing: TEntity | None,
        entity: TEntity,
    ) -> TEntity:
        """Add an entity to the repository only when it is newly created.

        Args:
            repository: Repository that owns the entity type.
            existing: Existing entity matched by Notion ID, if any.
            entity: Newly mapped entity instance.

        Returns:
            The entity passed in, whether newly added or pre-existing.

        """
        if existing is None:
            repository.add(entity)
        return entity
