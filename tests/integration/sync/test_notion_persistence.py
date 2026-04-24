"""Tests for the Notion persistence and repository layers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.persistence_service import (
    NotionPersistenceService,
)
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
    Workout,
)
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository

pytestmark = pytest.mark.integration

def _nutrition_schema(
    notion_id: str = "nutrition-1",
    name: str = "Performance Fueling",
    **kwargs: dict[str, Any],
) -> NotionNutritionGuideline:
    defaults = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionNutritionGuideline(**defaults)  # pyright: ignore[reportArgumentType]


def _phase_schema(
    notion_id: str = "phase-1", name: str = "Base Phase", **kwargs: dict[str, Any]
) -> NotionPhase:
    defaults = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionPhase(**defaults)  # pyright: ignore[reportArgumentType]


def _plan_schema(
    notion_id: str = "plan-1", name: str = "Base Plan", **kwargs: dict[str, Any]
) -> NotionPlan:
    defaults = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionPlan(**defaults)  # pyright: ignore[reportArgumentType]


def _workout_schema(
    notion_id: str = "workout-1",
    name: str = "Long Run",
    **kwargs: dict[str, Any],
) -> NotionWorkout:
    defaults = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionWorkout(**defaults)  # pyright: ignore[reportArgumentType]


def _event_schema(
    notion_id: str = "event-1", name: str = "Goal Race", **kwargs: dict[str, Any]
) -> NotionEvent:
    defaults = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionEvent(**defaults)  # pyright: ignore[reportArgumentType]


def _session_schema(
    notion_id: str = "session-1",
    name: str = "Morning Run",
    **kwargs: dict[str, Any],
) -> NotionSession:
    defaults = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionSession(**defaults)  # pyright: ignore[reportArgumentType]


def _feedback_schema(
    notion_id: str = "feedback-1",
    week: str = "2024-W10",
    **kwargs: dict[str, Any],
) -> NotionWeeklyFeedback:
    defaults = {
        "notion_id": notion_id,
        "name": week,
        "week": week,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionWeeklyFeedback(**defaults)  # pyright: ignore[reportArgumentType]


def _phase_entity(notion_id: str, name: str = "Base Phase") -> Phase:
    entity = Phase()
    entity.notion_page_id = notion_id
    entity.notion_url = f"https://notion.so/{notion_id}"
    entity.name = name
    return entity


def _workout_entity(notion_id: str, name: str = "Long Run") -> Workout:
    entity = Workout()
    entity.notion_page_id = notion_id
    entity.notion_url = f"https://notion.so/{notion_id}"
    entity.name = name
    return entity


def _session_entity(notion_id: str, name: str = "Morning Run") -> TrackedSession:
    entity = TrackedSession()
    entity.notion_page_id = notion_id
    entity.notion_url = f"https://notion.so/{notion_id}"
    entity.name = name
    return entity


def _feedback_entity(notion_id: str, week: str = "2024-W10") -> Feedback:
    entity = Feedback()
    entity.notion_page_id = notion_id
    entity.notion_url = f"https://notion.so/{notion_id}"
    entity.week = week
    return entity


class TestBaseRepositoryWithPhase:
    def test_get_by_notion_id_returns_none_when_not_found(self, db_session: Session) -> None:
        repo = TrainingBaseRepository[Phase](db_session, Phase)

        assert repo.get_by_source_page_id("missing") is None

    def test_add_persists_entity(self, db_session: Session) -> None:
        repo = TrainingBaseRepository[Phase](db_session, Phase)
        entity = repo.add(_phase_entity("phase-added"))
        db_session.flush()

        assert entity.id is not None
        assert repo.get_by_source_page_id("phase-added") is entity


class TestBaseRepositoryWithWorkout:
    def test_get_by_notion_id_returns_none_when_not_found(self, db_session: Session) -> None:
        repo = TrainingBaseRepository[Workout](db_session, Workout)

        assert repo.get_by_source_page_id("missing") is None

    def test_add_persists_entity(self, db_session: Session) -> None:
        repo = TrainingBaseRepository[Workout](db_session, Workout)
        entity = repo.add(_workout_entity("workout-added"))
        db_session.flush()

        assert entity.id is not None
        assert repo.get_by_source_page_id("workout-added") is entity


class TestBaseRepositoryWithTrackedSession:
    def test_get_by_notion_id_returns_none_when_not_found(self, db_session: Session) -> None:
        repo = TrainingBaseRepository[TrackedSession](db_session, TrackedSession)

        assert repo.get_by_source_page_id("missing") is None

    def test_add_persists_entity(self, db_session: Session) -> None:
        repo = TrainingBaseRepository[TrackedSession](db_session, TrackedSession)
        entity = repo.add(_session_entity("session-added"))
        db_session.flush()

        assert entity.id is not None
        assert repo.get_by_source_page_id("session-added") is entity


class TestBaseRepositoryWithFeedback:
    def test_get_by_notion_id_returns_none_when_not_found(self, db_session: Session) -> None:
        repo = TrainingBaseRepository[Feedback](db_session, Feedback)

        assert repo.get_by_source_page_id("missing") is None

    def test_add_persists_entity(self, db_session: Session) -> None:
        repo = TrainingBaseRepository[Feedback](db_session, Feedback)
        entity = repo.add(_feedback_entity("feedback-added"))
        db_session.flush()

        assert entity.id is not None
        assert repo.get_by_source_page_id("feedback-added") is entity


class TestNotionPersistenceService:
    def test_persist_plans_inserts_new_rows(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        entities = svc.persist_plans([_plan_schema("pl-1"), _plan_schema("pl-2")])

        assert len(entities) == 2
        assert {entity.notion_page_id for entity in entities} == {"pl-1", "pl-2"}

    def test_persist_plans_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_plans([_plan_schema("pl-upd", name="Original")])
        original_id = original.id
        [updated] = svc.persist_plans([_plan_schema("pl-upd", name="Updated")])

        assert updated.id == original_id
        assert updated.name == "Updated"
        rows = (
            db_session.execute(select(Plan).where(Plan.notion_page_id == "pl-upd")).scalars().all()
        )
        assert len(rows) == 1

    def test_persist_nutrition_guidelines_updates_existing_rows_in_place(
        self, db_session: Session
    ) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_nutrition_guidelines(
            [_nutrition_schema("nutrition-upd", goal="Performance")]
        )
        original_id = original.id
        [updated] = svc.persist_nutrition_guidelines(
            [_nutrition_schema("nutrition-upd", goal="Gain")]
        )

        assert updated.id == original_id
        assert updated.goal == "Gain"
        rows = (
            db_session.execute(
                select(NutritionGuideline).where(
                    NutritionGuideline.notion_page_id == "nutrition-upd"
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1

    def test_persist_phases_resolves_nutrition_guideline_fk_by_notion_id(
        self, db_session: Session
    ) -> None:
        svc = NotionPersistenceService(db_session)

        [guideline] = svc.persist_nutrition_guidelines([_nutrition_schema("nutrition-parent")])
        [phase] = svc.persist_phases(
            [_phase_schema("phase-child", nutrition_guideline_notion_id="nutrition-parent")]
        )

        assert phase.nutrition_guideline_id == guideline.id

<<<<<<< HEAD
    def test_persist_phases_resolves_plan_fk_by_notion_id(self, session: Session) -> None:
        svc = NotionPersistenceService(session)
=======

    def test_persist_phases_resolves_plan_fk_by_notion_id(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)
>>>>>>> dca8fae (fix: switch integration and API test fixtures from SQLite to postgres_test)

        [plan] = svc.persist_plans([_plan_schema("plan-parent")])
        [phase] = svc.persist_phases([_phase_schema("phase-child", plan_notion_id="plan-parent")])

        assert phase.plan_id == plan.id

    def test_persist_phases_inserts_new_rows(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        entities = svc.persist_phases([_phase_schema("ph-1"), _phase_schema("ph-2")])

        assert len(entities) == 2
        assert {entity.notion_page_id for entity in entities} == {"ph-1", "ph-2"}

    def test_persist_phases_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_phases([_phase_schema("ph-upd", name="Original")])
        original_id = original.id
        [updated] = svc.persist_phases([_phase_schema("ph-upd", name="Updated")])

        assert updated.id == original_id
        assert updated.name == "Updated"
        rows = (
            db_session.execute(
                select(Phase).where(Phase.notion_page_id == "ph-upd")
            ).scalars().all()
        )
        assert len(rows) == 1

    def test_persist_workouts_resolves_phase_fk_by_notion_id(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [phase] = svc.persist_phases([_phase_schema("phase-parent")])
        [workout] = svc.persist_workouts(
            [_workout_schema("workout-child", phase_notion_id="phase-parent")]
        )

        assert workout.phase_id == phase.id

    def test_persist_workouts_stores_current_workout_fields(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [workout] = svc.persist_workouts(
            [
                _workout_schema(
                    "wo-fields",
                    planned_training_load=410.0,
                    actual_duration_min=58.0,
                    actual_distance_km=10.2,
                    actual_training_load=438.0,
                    actual_calories_burned_kcal=720.0,
                    weighted_hrr_intensity_sum=145.5,
                    actual_hrr_intensity=2.51,
                    done_date_start="2024-03-01T08:00:00+00:00",
                    done_date_end=None,
                    done_date_is_datetime=True,
                    status="Done",
                    training_load_method="Weighted HRR",
                )
            ]
        )

        assert workout.planned_training_load == pytest.approx(410.0)
        assert workout.actual_duration_min == pytest.approx(58.0)
        assert workout.actual_distance_km == pytest.approx(10.2)
        assert workout.actual_training_load == pytest.approx(438.0)
        assert workout.actual_calories_burned_kcal == pytest.approx(720.0)
        assert workout.weighted_hrr_intensity_sum == pytest.approx(145.5)
        assert workout.actual_hrr_intensity == pytest.approx(2.51)
        assert workout.done_date_start == datetime(2024, 3, 1, 8, 0, tzinfo=UTC)
        assert workout.done_date_is_datetime is True
        assert workout.status == "Done"
        assert workout.training_load_method == "Weighted HRR"

    def test_persist_workouts_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_workouts([_workout_schema("wo-upd", name="Old Name")])
        original_id = original.id
        [updated] = svc.persist_workouts([_workout_schema("wo-upd", name="New Name")])

        assert updated.id == original_id
        assert updated.name == "New Name"
        rows = (
            db_session.execute(select(Workout).where(Workout.notion_page_id == "wo-upd"))
            .scalars()
            .all()
        )
        assert len(rows) == 1

    def test_persist_events_resolves_plan_and_workout_fks(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [plan] = svc.persist_plans([_plan_schema("plan-parent")])
        svc.persist_phases([_phase_schema("phase-parent")])
        [workout] = svc.persist_workouts(
            [_workout_schema("workout-parent", phase_notion_id="phase-parent")]
        )
        [event_entity] = svc.persist_events(
            [
                _event_schema(
                    "event-child",
                    plan_notion_id="plan-parent",
                    race_workout_notion_id="workout-parent",
                )
            ]
        )

        assert event_entity.plan_id == plan.id
        assert event_entity.race_workout_id == workout.id

    def test_persist_events_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_events([_event_schema("event-upd", priority="C")])
        original_id = original.id
        [updated] = svc.persist_events([_event_schema("event-upd", priority="A")])

        assert updated.id == original_id
        assert updated.priority == "A"
        rows = (
            db_session.execute(select(Event).where(Event.notion_page_id == "event-upd"))
            .scalars()
            .all()
        )
        assert len(rows) == 1

<<<<<<< HEAD
    def test_persist_sessions_resolves_workout_fk_by_notion_id(self, session: Session) -> None:
        svc = NotionPersistenceService(session)
=======

    def test_persist_sessions_resolves_workout_fk_by_notion_id(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)
>>>>>>> dca8fae (fix: switch integration and API test fixtures from SQLite to postgres_test)

        [workout] = svc.persist_workouts([_workout_schema("workout-parent")])
        [tracked] = svc.persist_sessions(
            [_session_schema("session-child", workout_notion_id="workout-parent")]
        )

        assert tracked.workout_id == workout.id

    def test_persist_sessions_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_sessions([_session_schema("sess-upd", name="Old")])
        original_id = original.id
        [updated] = svc.persist_sessions([_session_schema("sess-upd", name="New")])

        assert updated.id == original_id
        assert updated.name == "New"
        rows = (
            db_session.execute(
                select(TrackedSession).where(TrackedSession.notion_page_id == "sess-upd")
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1

    def test_persist_feedback_resolves_phase_fk_by_notion_id(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [phase] = svc.persist_phases([_phase_schema("phase-for-feedback")])
        [feedback] = svc.persist_feedback(
            [_feedback_schema("feedback-child", phase_notion_id="phase-for-feedback")]
        )

        assert feedback.phase_id == phase.id

    def test_persist_feedback_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_feedback([_feedback_schema("fb-upd", week="2024-W10")])
        original_id = original.id
        [updated] = svc.persist_feedback([_feedback_schema("fb-upd", week="2024-W11")])

        assert updated.id == original_id
        assert updated.week == "2024-W11"
        rows = (
            db_session.execute(select(Feedback).where(Feedback.notion_page_id == "fb-upd"))
            .scalars()
            .all()
        )
        assert len(rows) == 1

    def test_persist_all_persists_all_entity_types_in_dependency_order(
        self, db_session: Session
    ) -> None:
        svc = NotionPersistenceService(db_session)

        svc.persist_all(
            plan_schemas=[_plan_schema("dep-plan")],
            nutrition_guideline_schemas=[],
            phase_schemas=[_phase_schema("dep-phase", plan_notion_id="dep-plan")],
            workout_schemas=[_workout_schema("dep-workout", phase_notion_id="dep-phase")],
            event_schemas=[],
            session_schemas=[_session_schema("dep-session", workout_notion_id="dep-workout")],
            feedback_schemas=[_feedback_schema("dep-feedback", phase_notion_id="dep-phase")],
        )

        plan = db_session.execute(
            select(Plan).where(Plan.notion_page_id == "dep-plan")
        ).scalar_one()
        phase = db_session.execute(
            select(Phase).where(Phase.notion_page_id == "dep-phase")
        ).scalar_one()
        workout = db_session.execute(
            select(Workout).where(Workout.notion_page_id == "dep-workout")
        ).scalar_one()
        tracked = db_session.execute(
            select(TrackedSession).where(TrackedSession.notion_page_id == "dep-session")
        ).scalar_one()
        feedback = db_session.execute(
            select(Feedback).where(Feedback.notion_page_id == "dep-feedback")
        ).scalar_one()

        assert phase.plan_id == plan.id
        assert workout.phase_id == phase.id
        assert tracked.workout_id == workout.id
        assert feedback.phase_id == phase.id

    def test_persist_all_stores_page_content_across_entities(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        svc.persist_all(
            plan_schemas=[_plan_schema("content-plan", notion_page_content="Plan body")],
            nutrition_guideline_schemas=[
                _nutrition_schema("content-nutrition", notion_page_content="Nutrition body")
            ],
            phase_schemas=[
                _phase_schema(
                    "content-phase",
                    plan_notion_id="content-plan",
                    nutrition_guideline_notion_id="content-nutrition",
                    notion_page_content="Phase body",
                )
            ],
            workout_schemas=[
                _workout_schema(
                    "content-workout",
                    phase_notion_id="content-phase",
                    notion_page_content="Workout body",
                )
            ],
            event_schemas=[
                _event_schema(
                    "content-event",
                    plan_notion_id="content-plan",
                    race_workout_notion_id="content-workout",
                    notion_page_content="Event body",
                )
            ],
            session_schemas=[
                _session_schema(
                    "content-session",
                    workout_notion_id="content-workout",
                    notion_page_content="Session body",
                )
            ],
            feedback_schemas=[
                _feedback_schema(
                    "content-feedback",
                    phase_notion_id="content-phase",
                    notion_page_content="Feedback body",
                )
            ],
        )

        plan = db_session.execute(
            select(Plan).where(Plan.notion_page_id == "content-plan")
        ).scalar_one()
        nutrition = db_session.execute(
            select(NutritionGuideline).where(
                NutritionGuideline.notion_page_id == "content-nutrition"
            )
        ).scalar_one()
        phase = db_session.execute(
            select(Phase).where(Phase.notion_page_id == "content-phase")
        ).scalar_one()
        workout = db_session.execute(
            select(Workout).where(Workout.notion_page_id == "content-workout")
        ).scalar_one()
        event_entity = db_session.execute(
            select(Event).where(Event.notion_page_id == "content-event")
        ).scalar_one()
        tracked = db_session.execute(
            select(TrackedSession).where(TrackedSession.notion_page_id == "content-session")
        ).scalar_one()
        feedback = db_session.execute(
            select(Feedback).where(Feedback.notion_page_id == "content-feedback")
        ).scalar_one()

        assert plan.notion_page_content == "Plan body"
        assert nutrition.notion_page_content == "Nutrition body"
        assert phase.notion_page_content == "Phase body"
        assert workout.notion_page_content == "Workout body"
        assert event_entity.notion_page_content == "Event body"
        assert tracked.notion_page_content == "Session body"
        assert feedback.notion_page_content == "Feedback body"

    def test_persist_all_is_idempotent_across_repeated_runs(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        svc.persist_all(
            plan_schemas=[_plan_schema("idem-plan", name="Plan v1")],
            nutrition_guideline_schemas=[],
            phase_schemas=[_phase_schema("idem-phase", name="Phase v1")],
            workout_schemas=[_workout_schema("idem-workout", name="Workout v1")],
            event_schemas=[],
            session_schemas=[_session_schema("idem-session", name="Session v1")],
            feedback_schemas=[_feedback_schema("idem-feedback", week="2024-W01")],
        )
        svc.persist_all(
            plan_schemas=[_plan_schema("idem-plan", name="Plan v2")],
            nutrition_guideline_schemas=[],
            phase_schemas=[_phase_schema("idem-phase", name="Phase v2")],
            workout_schemas=[_workout_schema("idem-workout", name="Workout v2")],
            event_schemas=[],
            session_schemas=[_session_schema("idem-session", name="Session v2")],
            feedback_schemas=[_feedback_schema("idem-feedback", week="2024-W02")],
        )

        plan_rows = (
            db_session.execute(
                select(Plan).where(Plan.notion_page_id == "idem-plan")
            ).scalars().all()
        )

        phase_rows = (
            db_session.execute(select(Phase).where(Phase.notion_page_id == "idem-phase"))
            .scalars()
            .all()
        )
        workout_rows = (
            db_session.execute(select(Workout).where(Workout.notion_page_id == "idem-workout"))
            .scalars()
            .all()
        )
        session_rows = (
            db_session.execute(
                select(TrackedSession).where(TrackedSession.notion_page_id == "idem-session")
            )
            .scalars()
            .all()
        )
        feedback_rows = (
            db_session.execute(select(Feedback).where(Feedback.notion_page_id == "idem-feedback"))
            .scalars()
            .all()
        )

        assert len(plan_rows) == 1
        assert len(phase_rows) == 1
        assert len(workout_rows) == 1
        assert len(session_rows) == 1
        assert len(feedback_rows) == 1
        assert plan_rows[0].name == "Plan v2"
        assert phase_rows[0].name == "Phase v2"
        assert workout_rows[0].name == "Workout v2"
        assert session_rows[0].name == "Session v2"
        assert feedback_rows[0].week == "2024-W02"

    def test_persist_all_empty_lists_completes_without_error(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        svc.persist_all(
            plan_schemas=[],
            nutrition_guideline_schemas=[],
            phase_schemas=[],
            workout_schemas=[],
            event_schemas=[],
            session_schemas=[],
            feedback_schemas=[],
        )
