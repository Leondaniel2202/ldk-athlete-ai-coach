"""Tests for the Notion persistence and repository layers."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.persistence_service import (
    NotionPersistenceService,
)
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
from tests.factories.notion_schemas import (
    make_notion_event,
    make_notion_nutrition_guideline,
    make_notion_phase,
    make_notion_plan,
    make_notion_session,
    make_notion_weekly_feedback,
    make_notion_workout,
)

pytestmark = pytest.mark.integration


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

        entities = svc.persist_plans([make_notion_plan("pl-1"), make_notion_plan("pl-2")])

        assert len(entities) == 2
        assert {entity.notion_page_id for entity in entities} == {"pl-1", "pl-2"}

    def test_persist_plans_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_plans([make_notion_plan("pl-upd", name="Original")])
        original_id = original.id
        [updated] = svc.persist_plans([make_notion_plan("pl-upd", name="Updated")])

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
            [make_notion_nutrition_guideline("nutrition-upd", goal="Performance")]
        )
        original_id = original.id
        [updated] = svc.persist_nutrition_guidelines(
            [make_notion_nutrition_guideline("nutrition-upd", goal="Gain")]
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

        [guideline] = svc.persist_nutrition_guidelines(
            [make_notion_nutrition_guideline("nutrition-parent")]
        )
        [phase] = svc.persist_phases(
            [make_notion_phase("phase-child", nutrition_guideline_notion_id="nutrition-parent")]
        )

        assert phase.nutrition_guideline_id == guideline.id

    def test_persist_phases_resolves_plan_fk_by_notion_id(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [plan] = svc.persist_plans([make_notion_plan("plan-parent")])
        [phase] = svc.persist_phases(
            [make_notion_phase("phase-child", plan_notion_id="plan-parent")]
        )

        assert phase.plan_id == plan.id

    def test_persist_phases_inserts_new_rows(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        entities = svc.persist_phases([make_notion_phase("ph-1"), make_notion_phase("ph-2")])

        assert len(entities) == 2
        assert {entity.notion_page_id for entity in entities} == {"ph-1", "ph-2"}

    def test_persist_phases_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_phases([make_notion_phase("ph-upd", name="Original")])
        original_id = original.id
        [updated] = svc.persist_phases([make_notion_phase("ph-upd", name="Updated")])

        assert updated.id == original_id
        assert updated.name == "Updated"
        rows = (
            db_session.execute(select(Phase).where(Phase.notion_page_id == "ph-upd"))
            .scalars()
            .all()
        )
        assert len(rows) == 1

    def test_persist_workouts_resolves_phase_fk_by_notion_id(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [phase] = svc.persist_phases([make_notion_phase("phase-parent")])
        [workout] = svc.persist_workouts(
            [make_notion_workout("workout-child", phase_notion_id="phase-parent")]
        )

        assert workout.phase_id == phase.id

    def test_persist_workouts_stores_current_workout_fields(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [workout] = svc.persist_workouts(
            [
                make_notion_workout(
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

        [original] = svc.persist_workouts([make_notion_workout("wo-upd", name="Old Name")])
        original_id = original.id
        [updated] = svc.persist_workouts([make_notion_workout("wo-upd", name="New Name")])

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

        [plan] = svc.persist_plans([make_notion_plan("plan-parent")])
        svc.persist_phases([make_notion_phase("phase-parent")])
        [workout] = svc.persist_workouts(
            [make_notion_workout("workout-parent", phase_notion_id="phase-parent")]
        )
        [event_entity] = svc.persist_events(
            [
                make_notion_event(
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

        [original] = svc.persist_events([make_notion_event("event-upd", priority="C")])
        original_id = original.id
        [updated] = svc.persist_events([make_notion_event("event-upd", priority="A")])

        assert updated.id == original_id
        assert updated.priority == "A"
        rows = (
            db_session.execute(select(Event).where(Event.notion_page_id == "event-upd"))
            .scalars()
            .all()
        )
        assert len(rows) == 1

    def test_persist_sessions_resolves_workout_fk_by_notion_id(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [workout] = svc.persist_workouts([make_notion_workout("workout-parent")])
        [tracked] = svc.persist_sessions(
            [make_notion_session("session-child", workout_notion_id="workout-parent")]
        )

        assert tracked.workout_id == workout.id

    def test_persist_sessions_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_sessions([make_notion_session("sess-upd", name="Old")])
        original_id = original.id
        [updated] = svc.persist_sessions([make_notion_session("sess-upd", name="New")])

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

        [phase] = svc.persist_phases([make_notion_phase("phase-for-feedback")])
        [feedback] = svc.persist_feedback(
            [
                make_notion_weekly_feedback(
                    "feedback-child",
                    phase_notion_id="phase-for-feedback",
                )
            ]
        )

        assert feedback.phase_id == phase.id

    def test_persist_feedback_updates_existing_rows_in_place(self, db_session: Session) -> None:
        svc = NotionPersistenceService(db_session)

        [original] = svc.persist_feedback([make_notion_weekly_feedback("fb-upd", week="2024-W10")])
        original_id = original.id
        [updated] = svc.persist_feedback([make_notion_weekly_feedback("fb-upd", week="2024-W11")])

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
            plan_schemas=[make_notion_plan("dep-plan")],
            nutrition_guideline_schemas=[],
            phase_schemas=[make_notion_phase("dep-phase", plan_notion_id="dep-plan")],
            workout_schemas=[make_notion_workout("dep-workout", phase_notion_id="dep-phase")],
            event_schemas=[],
            session_schemas=[make_notion_session("dep-session", workout_notion_id="dep-workout")],
            feedback_schemas=[
                make_notion_weekly_feedback("dep-feedback", phase_notion_id="dep-phase")
            ],
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
            plan_schemas=[make_notion_plan("content-plan", notion_page_content="Plan body")],
            nutrition_guideline_schemas=[
                make_notion_nutrition_guideline(
                    "content-nutrition",
                    notion_page_content="Nutrition body",
                )
            ],
            phase_schemas=[
                make_notion_phase(
                    "content-phase",
                    plan_notion_id="content-plan",
                    nutrition_guideline_notion_id="content-nutrition",
                    notion_page_content="Phase body",
                )
            ],
            workout_schemas=[
                make_notion_workout(
                    "content-workout",
                    phase_notion_id="content-phase",
                    notion_page_content="Workout body",
                )
            ],
            event_schemas=[
                make_notion_event(
                    "content-event",
                    plan_notion_id="content-plan",
                    race_workout_notion_id="content-workout",
                    notion_page_content="Event body",
                )
            ],
            session_schemas=[
                make_notion_session(
                    "content-session",
                    workout_notion_id="content-workout",
                    notion_page_content="Session body",
                )
            ],
            feedback_schemas=[
                make_notion_weekly_feedback(
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
            plan_schemas=[make_notion_plan("idem-plan", name="Plan v1")],
            nutrition_guideline_schemas=[],
            phase_schemas=[make_notion_phase("idem-phase", name="Phase v1")],
            workout_schemas=[make_notion_workout("idem-workout", name="Workout v1")],
            event_schemas=[],
            session_schemas=[make_notion_session("idem-session", name="Session v1")],
            feedback_schemas=[make_notion_weekly_feedback("idem-feedback", week="2024-W01")],
        )
        svc.persist_all(
            plan_schemas=[make_notion_plan("idem-plan", name="Plan v2")],
            nutrition_guideline_schemas=[],
            phase_schemas=[make_notion_phase("idem-phase", name="Phase v2")],
            workout_schemas=[make_notion_workout("idem-workout", name="Workout v2")],
            event_schemas=[],
            session_schemas=[make_notion_session("idem-session", name="Session v2")],
            feedback_schemas=[make_notion_weekly_feedback("idem-feedback", week="2024-W02")],
        )

        plan_rows = (
            db_session.execute(select(Plan).where(Plan.notion_page_id == "idem-plan"))
            .scalars()
            .all()
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
