"""Tests for the Notion persistence layer.

Uses an in-memory SQLite database so that no external infrastructure is
required.  All test schemas are created from minimal but valid Pydantic
instances matching the NotionSyncMixin constraints (notion_page_id and
notion_url are non-nullable and unique).
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.core.integrations.notion.persistence_service import (
    NotionPersistenceService,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_phase import NotionPhase
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_session import NotionSession
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_weekly_feedback import (
    NotionWeeklyFeedback,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout
from ldk_athlete_ai_coach.db.base import Base
from ldk_athlete_ai_coach.db.models.sport_manager import Feedback, Phase, TrackedSession, Workout
from ldk_athlete_ai_coach.db.repositories.feedback_repository import FeedbackRepository
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository

# ---------------------------------------------------------------------------
# In-memory SQLite engine + session fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def engine():
    """Create a shared in-memory SQLite engine with the full schema."""
    _engine = create_engine("sqlite:///:memory:")
    # Enable FK enforcement for SQLite (off by default)
    event.listen(
        _engine,
        "connect",
        lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"),
    )
    Base.metadata.create_all(_engine)
    yield _engine
    _engine.dispose()


@pytest.fixture()
def session(engine):
    """Yield a transactional session that is rolled back after each test.

    This keeps tests isolated without re-creating the schema for every test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    _session = Session(bind=connection)
    yield _session
    _session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# Schema factory helpers
# ---------------------------------------------------------------------------


def _phase_schema(notion_id: str = "phase-1", name: str = "Base Phase", **kwargs) -> NotionPhase:
    defaults = {
        "notion_id": notion_id,
        "name": name,
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionPhase(**defaults)


def _workout_schema(
    notion_id: str = "workout-1",
    name: str = "Long Run",
    **kwargs,
) -> NotionWorkout:
    defaults = {
        "notion_id": notion_id,
        "name": name,
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionWorkout(**defaults)


def _session_schema(
    notion_id: str = "session-1",
    name: str = "Morning Run",
    **kwargs,
) -> NotionSession:
    defaults = {
        "notion_id": notion_id,
        "name": name,
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionSession(**defaults)


def _feedback_schema(
    notion_id: str = "feedback-1",
    week: str = "2024-W10",
    **kwargs,
) -> NotionWeeklyFeedback:
    defaults = {
        "notion_id": notion_id,
        "week": week,
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionWeeklyFeedback(**defaults)


# ===========================================================================
# PhaseRepository
# ===========================================================================


class TestPhaseRepository:
    def test_get_by_notion_id_returns_none_when_not_found(self, session: Session) -> None:
        repo = PhaseRepository(session)
        assert repo.get_by_notion_id("nonexistent-id") is None

    def test_upsert_inserts_new_row(self, session: Session) -> None:
        repo = PhaseRepository(session)
        schema = _phase_schema(notion_id="phase-new", name="Base Phase")

        entity = repo.upsert(schema)
        session.flush()

        assert isinstance(entity, Phase)
        assert entity.notion_page_id == "phase-new"
        assert entity.name == "Base Phase"
        assert entity.id is not None

    def test_upsert_updates_existing_row(self, session: Session) -> None:
        repo = PhaseRepository(session)
        schema_v1 = _phase_schema(notion_id="phase-upd", name="Original")
        entity_v1 = repo.upsert(schema_v1)
        session.flush()
        original_id = entity_v1.id

        schema_v2 = _phase_schema(notion_id="phase-upd", name="Updated")
        entity_v2 = repo.upsert(schema_v2)
        session.flush()

        # Same DB row – same primary key
        assert entity_v2.id == original_id
        assert entity_v2.name == "Updated"

    def test_upsert_is_idempotent(self, session: Session) -> None:
        repo = PhaseRepository(session)
        schema = _phase_schema(notion_id="phase-idem")

        repo.upsert(schema)
        repo.upsert(schema)
        session.flush()

        from sqlalchemy import select

        rows = session.execute(
            select(Phase).where(Phase.notion_page_id == "phase-idem")
        ).scalars().all()
        assert len(rows) == 1

    def test_get_by_notion_id_returns_inserted_entity(self, session: Session) -> None:
        repo = PhaseRepository(session)
        schema = _phase_schema(notion_id="phase-lookup")
        repo.upsert(schema)
        session.flush()

        found = repo.get_by_notion_id("phase-lookup")

        assert found is not None
        assert found.notion_page_id == "phase-lookup"

    def test_upsert_with_no_fk_ids_sets_them_to_none(self, session: Session) -> None:
        repo = PhaseRepository(session)
        schema = _phase_schema(notion_id="phase-nofk")
        entity = repo.upsert(schema)
        session.flush()

        assert entity.plan_id is None
        assert entity.nutrition_guideline_id is None


# ===========================================================================
# WorkoutRepository
# ===========================================================================


class TestWorkoutRepository:
    def test_get_by_notion_id_returns_none_when_not_found(self, session: Session) -> None:
        repo = WorkoutRepository(session)
        assert repo.get_by_notion_id("missing") is None

    def test_upsert_inserts_new_row(self, session: Session) -> None:
        repo = WorkoutRepository(session)
        schema = _workout_schema(notion_id="wo-new", name="Intervals")

        entity = repo.upsert(schema)
        session.flush()

        assert isinstance(entity, Workout)
        assert entity.notion_page_id == "wo-new"
        assert entity.name == "Intervals"
        assert entity.id is not None

    def test_upsert_updates_existing_row(self, session: Session) -> None:
        repo = WorkoutRepository(session)
        schema_v1 = _workout_schema(notion_id="wo-upd", name="Old Name")
        entity_v1 = repo.upsert(schema_v1)
        session.flush()
        original_id = entity_v1.id

        schema_v2 = _workout_schema(notion_id="wo-upd", name="New Name")
        entity_v2 = repo.upsert(schema_v2)
        session.flush()

        assert entity_v2.id == original_id
        assert entity_v2.name == "New Name"

    def test_upsert_is_idempotent(self, session: Session) -> None:
        repo = WorkoutRepository(session)
        schema = _workout_schema(notion_id="wo-idem")

        repo.upsert(schema)
        repo.upsert(schema)
        session.flush()

        from sqlalchemy import select

        rows = session.execute(
            select(Workout).where(Workout.notion_page_id == "wo-idem")
        ).scalars().all()
        assert len(rows) == 1

    def test_upsert_assigns_phase_id(self, session: Session) -> None:
        phase_repo = PhaseRepository(session)
        phase = phase_repo.upsert(_phase_schema(notion_id="ph-for-wo"))
        session.flush()
        assert phase.id is not None

        repo = WorkoutRepository(session)
        entity = repo.upsert(_workout_schema(notion_id="wo-with-ph"), phase_id=phase.id)
        session.flush()

        assert entity.phase_id == phase.id

    def test_get_by_notion_id_returns_inserted_entity(self, session: Session) -> None:
        repo = WorkoutRepository(session)
        repo.upsert(_workout_schema(notion_id="wo-lookup"))
        session.flush()

        found = repo.get_by_notion_id("wo-lookup")

        assert found is not None
        assert found.notion_page_id == "wo-lookup"


# ===========================================================================
# SessionRepository
# ===========================================================================


class TestSessionRepository:
    def test_get_by_notion_id_returns_none_when_not_found(self, session: Session) -> None:
        repo = SessionRepository(session)
        assert repo.get_by_notion_id("missing") is None

    def test_upsert_inserts_new_row(self, session: Session) -> None:
        repo = SessionRepository(session)
        schema = _session_schema(notion_id="sess-new", name="Evening Run")

        entity = repo.upsert(schema)
        session.flush()

        assert isinstance(entity, TrackedSession)
        assert entity.notion_page_id == "sess-new"
        assert entity.name == "Evening Run"
        assert entity.id is not None

    def test_upsert_updates_existing_row(self, session: Session) -> None:
        repo = SessionRepository(session)
        entity_v1 = repo.upsert(_session_schema(notion_id="sess-upd", name="Old"))
        session.flush()
        original_id = entity_v1.id

        entity_v2 = repo.upsert(_session_schema(notion_id="sess-upd", name="New"))
        session.flush()

        assert entity_v2.id == original_id
        assert entity_v2.name == "New"

    def test_upsert_is_idempotent(self, session: Session) -> None:
        repo = SessionRepository(session)
        schema = _session_schema(notion_id="sess-idem")

        repo.upsert(schema)
        repo.upsert(schema)
        session.flush()

        from sqlalchemy import select

        rows = session.execute(
            select(TrackedSession).where(TrackedSession.notion_page_id == "sess-idem")
        ).scalars().all()
        assert len(rows) == 1

    def test_upsert_assigns_workout_id(self, session: Session) -> None:
        wo_repo = WorkoutRepository(session)
        workout = wo_repo.upsert(_workout_schema(notion_id="wo-for-sess"))
        session.flush()
        assert workout.id is not None

        repo = SessionRepository(session)
        entity = repo.upsert(_session_schema(notion_id="sess-with-wo"), workout_id=workout.id)
        session.flush()

        assert entity.workout_id == workout.id

    def test_get_by_notion_id_returns_inserted_entity(self, session: Session) -> None:
        repo = SessionRepository(session)
        repo.upsert(_session_schema(notion_id="sess-lookup"))
        session.flush()

        found = repo.get_by_notion_id("sess-lookup")

        assert found is not None
        assert found.notion_page_id == "sess-lookup"


# ===========================================================================
# FeedbackRepository
# ===========================================================================


class TestFeedbackRepository:
    def test_get_by_notion_id_returns_none_when_not_found(self, session: Session) -> None:
        repo = FeedbackRepository(session)
        assert repo.get_by_notion_id("missing") is None

    def test_upsert_inserts_new_row(self, session: Session) -> None:
        repo = FeedbackRepository(session)
        schema = _feedback_schema(notion_id="fb-new", week="2024-W10")

        entity = repo.upsert(schema)
        session.flush()

        assert isinstance(entity, Feedback)
        assert entity.notion_page_id == "fb-new"
        assert entity.week == "2024-W10"
        assert entity.id is not None

    def test_upsert_updates_existing_row(self, session: Session) -> None:
        repo = FeedbackRepository(session)
        entity_v1 = repo.upsert(_feedback_schema(notion_id="fb-upd", week="2024-W10"))
        session.flush()
        original_id = entity_v1.id

        entity_v2 = repo.upsert(_feedback_schema(notion_id="fb-upd", week="2024-W11"))
        session.flush()

        assert entity_v2.id == original_id
        assert entity_v2.week == "2024-W11"

    def test_upsert_is_idempotent(self, session: Session) -> None:
        repo = FeedbackRepository(session)
        schema = _feedback_schema(notion_id="fb-idem")

        repo.upsert(schema)
        repo.upsert(schema)
        session.flush()

        from sqlalchemy import select

        rows = session.execute(
            select(Feedback).where(Feedback.notion_page_id == "fb-idem")
        ).scalars().all()
        assert len(rows) == 1

    def test_upsert_assigns_phase_id(self, session: Session) -> None:
        phase_repo = PhaseRepository(session)
        phase = phase_repo.upsert(_phase_schema(notion_id="ph-for-fb"))
        session.flush()
        assert phase.id is not None

        repo = FeedbackRepository(session)
        entity = repo.upsert(_feedback_schema(notion_id="fb-with-ph"), phase_id=phase.id)
        session.flush()

        assert entity.phase_id == phase.id

    def test_get_by_notion_id_returns_inserted_entity(self, session: Session) -> None:
        repo = FeedbackRepository(session)
        repo.upsert(_feedback_schema(notion_id="fb-lookup"))
        session.flush()

        found = repo.get_by_notion_id("fb-lookup")

        assert found is not None
        assert found.notion_page_id == "fb-lookup"


# ===========================================================================
# NotionPersistenceService
# ===========================================================================


class TestNotionPersistenceService:
    # ------------------------------------------------------------------
    # persist_phases
    # ------------------------------------------------------------------

    def test_persist_phases_inserts_new_rows(self, session: Session) -> None:
        svc = NotionPersistenceService(session)
        schemas = [_phase_schema("ph-svc-1"), _phase_schema("ph-svc-2")]

        entities = svc.persist_phases(schemas)

        assert len(entities) == 2
        assert all(isinstance(e, Phase) for e in entities)
        assert {e.notion_page_id for e in entities} == {"ph-svc-1", "ph-svc-2"}

    def test_persist_phases_is_idempotent(self, session: Session) -> None:
        svc = NotionPersistenceService(session)
        schema = _phase_schema("ph-svc-idem", name="Original")

        svc.persist_phases([schema])
        svc.persist_phases([_phase_schema("ph-svc-idem", name="Updated")])

        from sqlalchemy import select

        rows = session.execute(
            select(Phase).where(Phase.notion_page_id == "ph-svc-idem")
        ).scalars().all()
        assert len(rows) == 1
        assert rows[0].name == "Updated"

    # ------------------------------------------------------------------
    # persist_workouts (FK resolution)
    # ------------------------------------------------------------------

    def test_persist_workouts_resolves_phase_fk(self, session: Session) -> None:
        svc = NotionPersistenceService(session)

        phase_schema = _phase_schema("ph-fk-1")
        [phase] = svc.persist_phases([phase_schema])
        assert phase.id is not None

        workout_schema = _workout_schema("wo-fk-1", phase_notion_id="ph-fk-1")
        [workout] = svc.persist_workouts([workout_schema])

        assert workout.phase_id == phase.id

    def test_persist_workouts_sets_phase_id_to_none_when_parent_missing(
        self, session: Session
    ) -> None:
        svc = NotionPersistenceService(session)
        workout_schema = _workout_schema("wo-no-phase", phase_notion_id="ghost-phase")

        [workout] = svc.persist_workouts([workout_schema])

        assert workout.phase_id is None

    def test_persist_workouts_sets_phase_id_to_none_when_no_relation(
        self, session: Session
    ) -> None:
        svc = NotionPersistenceService(session)
        workout_schema = _workout_schema("wo-null-phase")

        [workout] = svc.persist_workouts([workout_schema])

        assert workout.phase_id is None

    # ------------------------------------------------------------------
    # persist_sessions (FK resolution)
    # ------------------------------------------------------------------

    def test_persist_sessions_resolves_workout_fk(self, session: Session) -> None:
        svc = NotionPersistenceService(session)

        [workout] = svc.persist_workouts([_workout_schema("wo-for-sess-fk")])
        assert workout.id is not None

        session_schema = _session_schema("sess-fk-1", workout_notion_id="wo-for-sess-fk")
        [tracked] = svc.persist_sessions([session_schema])

        assert tracked.workout_id == workout.id

    def test_persist_sessions_sets_workout_id_to_none_when_parent_missing(
        self, session: Session
    ) -> None:
        svc = NotionPersistenceService(session)
        session_schema = _session_schema("sess-no-wo", workout_notion_id="ghost-workout")

        [tracked] = svc.persist_sessions([session_schema])

        assert tracked.workout_id is None

    # ------------------------------------------------------------------
    # persist_feedback (FK resolution)
    # ------------------------------------------------------------------

    def test_persist_feedback_resolves_phase_fk(self, session: Session) -> None:
        svc = NotionPersistenceService(session)

        [phase] = svc.persist_phases([_phase_schema("ph-for-fb-fk")])
        assert phase.id is not None

        feedback_schema = _feedback_schema("fb-fk-1", phase_notion_id="ph-for-fb-fk")
        [feedback] = svc.persist_feedback([feedback_schema])

        assert feedback.phase_id == phase.id

    def test_persist_feedback_sets_phase_id_to_none_when_parent_missing(
        self, session: Session
    ) -> None:
        svc = NotionPersistenceService(session)
        feedback_schema = _feedback_schema("fb-no-phase", phase_notion_id="ghost-phase")

        [feedback] = svc.persist_feedback([feedback_schema])

        assert feedback.phase_id is None

    # ------------------------------------------------------------------
    # persist_all (full transaction)
    # ------------------------------------------------------------------

    def test_persist_all_persists_all_entity_types(self, session: Session) -> None:
        svc = NotionPersistenceService(session)

        svc.persist_all(
            phase_schemas=[_phase_schema("pa-ph-1")],
            workout_schemas=[_workout_schema("pa-wo-1", phase_notion_id="pa-ph-1")],
            session_schemas=[_session_schema("pa-sess-1", workout_notion_id="pa-wo-1")],
            feedback_schemas=[_feedback_schema("pa-fb-1", phase_notion_id="pa-ph-1")],
        )

        from sqlalchemy import select

        assert session.execute(
            select(Phase).where(Phase.notion_page_id == "pa-ph-1")
        ).scalar_one_or_none() is not None
        assert session.execute(
            select(Workout).where(Workout.notion_page_id == "pa-wo-1")
        ).scalar_one_or_none() is not None
        assert session.execute(
            select(TrackedSession).where(TrackedSession.notion_page_id == "pa-sess-1")
        ).scalar_one_or_none() is not None
        assert session.execute(
            select(Feedback).where(Feedback.notion_page_id == "pa-fb-1")
        ).scalar_one_or_none() is not None

    def test_persist_all_resolves_relationships_in_dependency_order(
        self, session: Session
    ) -> None:
        svc = NotionPersistenceService(session)

        svc.persist_all(
            phase_schemas=[_phase_schema("dep-ph-1")],
            workout_schemas=[_workout_schema("dep-wo-1", phase_notion_id="dep-ph-1")],
            session_schemas=[_session_schema("dep-sess-1", workout_notion_id="dep-wo-1")],
            feedback_schemas=[_feedback_schema("dep-fb-1", phase_notion_id="dep-ph-1")],
        )

        from sqlalchemy import select

        phase = session.execute(
            select(Phase).where(Phase.notion_page_id == "dep-ph-1")
        ).scalar_one()
        workout = session.execute(
            select(Workout).where(Workout.notion_page_id == "dep-wo-1")
        ).scalar_one()
        tracked = session.execute(
            select(TrackedSession).where(TrackedSession.notion_page_id == "dep-sess-1")
        ).scalar_one()
        feedback = session.execute(
            select(Feedback).where(Feedback.notion_page_id == "dep-fb-1")
        ).scalar_one()

        assert workout.phase_id == phase.id
        assert tracked.workout_id == workout.id
        assert feedback.phase_id == phase.id

    def test_persist_all_is_idempotent_across_repeated_runs(self, session: Session) -> None:
        svc = NotionPersistenceService(session)
        kwargs = dict(
            phase_schemas=[_phase_schema("idem-ph-1", name="Phase v1")],
            workout_schemas=[_workout_schema("idem-wo-1", name="Workout v1")],
            session_schemas=[_session_schema("idem-sess-1", name="Session v1")],
            feedback_schemas=[_feedback_schema("idem-fb-1", week="2024-W01")],
        )

        svc.persist_all(**kwargs)

        # Second run with updated values
        svc.persist_all(
            phase_schemas=[_phase_schema("idem-ph-1", name="Phase v2")],
            workout_schemas=[_workout_schema("idem-wo-1", name="Workout v2")],
            session_schemas=[_session_schema("idem-sess-1", name="Session v2")],
            feedback_schemas=[_feedback_schema("idem-fb-1", week="2024-W02")],
        )

        from sqlalchemy import select

        phases = session.execute(select(Phase)).scalars().all()
        workouts = session.execute(select(Workout)).scalars().all()
        sessions = session.execute(select(TrackedSession)).scalars().all()
        feedbacks = session.execute(select(Feedback)).scalars().all()

        # No duplicates
        ph = [p for p in phases if p.notion_page_id == "idem-ph-1"]
        wo = [w for w in workouts if w.notion_page_id == "idem-wo-1"]
        se = [s for s in sessions if s.notion_page_id == "idem-sess-1"]
        fb = [f for f in feedbacks if f.notion_page_id == "idem-fb-1"]

        assert len(ph) == 1
        assert len(wo) == 1
        assert len(se) == 1
        assert len(fb) == 1

        # Updated values applied (Notion is source of truth)
        assert ph[0].name == "Phase v2"
        assert wo[0].name == "Workout v2"
        assert se[0].name == "Session v2"
        assert fb[0].week == "2024-W02"

    def test_persist_all_empty_lists_completes_without_error(self, session: Session) -> None:
        svc = NotionPersistenceService(session)
        svc.persist_all(
            phase_schemas=[],
            workout_schemas=[],
            session_schemas=[],
            feedback_schemas=[],
        )
