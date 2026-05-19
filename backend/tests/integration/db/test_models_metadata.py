"""Metadata registration tests for Sport Manager SQLAlchemy models."""

from __future__ import annotations

import pytest
from sqlalchemy import UniqueConstraint

import ldk_athlete_ai_coach.db.models  # noqa: F401
from ldk_athlete_ai_coach.db.base import Base

pytestmark = pytest.mark.integration


def test_sport_manager_models_register_expected_tables() -> None:
    """Ensure the approved Sport Manager tables are registered in metadata."""
    expected_tables = {
        "phases",
        "nutrition_guidelines",
        "workouts",
        "tracked_sessions",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())
    assert "athlete_dashboards" not in Base.metadata.tables
    assert "workout_phases" not in Base.metadata.tables
    assert "tracked_session_workouts" not in Base.metadata.tables


def test_sport_manager_foreign_keys_are_exposed_in_metadata() -> None:
    """Ensure key foreign-key relationships are visible to Alembic."""
    phases = Base.metadata.tables["phases"]
    workouts = Base.metadata.tables["workouts"]
    tracked_sessions = Base.metadata.tables["tracked_sessions"]
    feedback = Base.metadata.tables["feedback"]
    events = Base.metadata.tables["events"]

    assert "plan_id" not in Base.metadata.tables["plans"].c
    assert "primary_event_id" not in Base.metadata.tables["plans"].c
    assert "parent_phase_id" not in phases.c
    assert "notes" not in phases.c
    assert "timeframe_start" not in phases.c
    assert "timeframe_end" not in phases.c
    assert "timeframe_is_datetime" not in phases.c
    assert {"description", "start_date", "end_date"}.issubset(phases.c.keys())
    assert phases.c.phase_type.nullable is False
    assert phases.c.start_date.nullable is False
    assert phases.c.end_date.nullable is False
    assert {fk.target_fullname for fk in events.c.plan_id.foreign_keys} == {"plans.id"}
    assert {fk.target_fullname for fk in events.c.race_workout_id.foreign_keys} == {"workouts.id"}
    assert not any(
        constraint.columns.keys() == ["plan_id"]
        for constraint in events.constraints
        if isinstance(constraint, UniqueConstraint)
    )
    assert {fk.target_fullname for fk in workouts.c.phase_id.foreign_keys} == {"phases.id"}
    assert {fk.target_fullname for fk in tracked_sessions.c.workout_id.foreign_keys} == {
        "workouts.id"
    }
    assert {fk.target_fullname for fk in feedback.c.phase_id.foreign_keys} == {"phases.id"}
