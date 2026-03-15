"""Metadata registration tests for Sport Manager SQLAlchemy models."""

import ldk_athlete_ai_coach.db.models  # noqa: F401
from ldk_athlete_ai_coach.db.base import Base


def test_sport_manager_models_register_expected_tables() -> None:
    """Ensure the approved Sport Manager tables are registered in metadata."""
    expected_tables = {
        "events",
        "plans",
        "phases",
        "nutrition_guidelines",
        "workouts",
        "tracked_sessions",
        "training_loads",
        "feedback",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())
    assert "athlete_dashboards" not in Base.metadata.tables
    assert "workout_phases" not in Base.metadata.tables
    assert "tracked_session_workouts" not in Base.metadata.tables


def test_sport_manager_foreign_keys_are_exposed_in_metadata() -> None:
    """Ensure key foreign-key relationships are visible to Alembic."""
    events = Base.metadata.tables["events"]
    plans = Base.metadata.tables["plans"]
    phases = Base.metadata.tables["phases"]
    workouts = Base.metadata.tables["workouts"]
    tracked_sessions = Base.metadata.tables["tracked_sessions"]
    feedback = Base.metadata.tables["feedback"]

    assert {fk.target_fullname for fk in events.c.plan_id.foreign_keys} == {"plans.id"}
    assert {fk.target_fullname for fk in plans.c.primary_event_id.foreign_keys} == {"events.id"}
    assert {fk.target_fullname for fk in phases.c.parent_phase_id.foreign_keys} == {"phases.id"}
    assert {fk.target_fullname for fk in workouts.c.phase_id.foreign_keys} == {"phases.id"}
    assert {fk.target_fullname for fk in tracked_sessions.c.workout_id.foreign_keys} == {
        "workouts.id"
    }
    assert {fk.target_fullname for fk in feedback.c.phase_id.foreign_keys} == {"phases.id"}
