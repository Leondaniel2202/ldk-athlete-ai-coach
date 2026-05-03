"""Tests for the workout-context application service."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session
from tests.factories.persisted_training_models import (
    create_phase,
    create_plan,
    create_tracked_session,
    create_workout,
)

from ldk_athlete_ai_coach.application.services.workout_context_service import (
    WorkoutContextService,
)
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository

pytestmark = pytest.mark.integration


def _make_service(db: Session) -> WorkoutContextService:
    return WorkoutContextService(
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )


def test_service_returns_specific_workout_context_with_plan_phase_and_sessions(
    db_session: Session,
) -> None:
    """The service returns the requested workout with its related training context."""
    plan = create_plan(
        db_session,
        name="Workout Context Plan",
        start_date_start=datetime(2026, 4, 1, tzinfo=UTC),
        end_date_start=datetime(2026, 5, 1, tzinfo=UTC),
    )
    phase = create_phase(
        db_session,
        name="Workout Context Phase",
        plan=plan,
        phase_type="Build",
        timeframe_start=datetime(2026, 4, 6, tzinfo=UTC),
        timeframe_end=datetime(2026, 5, 1, tzinfo=UTC),
    )
    workout = create_workout(
        db_session,
        phase,
        name="Workout Context Run",
        date_start=datetime(2026, 4, 14, 7, 0, tzinfo=UTC),
        done_date_start=datetime(2026, 4, 14, 8, 0, tzinfo=UTC),
        status="Done",
        category="Run",
    )
    tracked_session = create_tracked_session(
        db_session,
        workout=workout,
        name="Workout Context Session",
        start=datetime(2026, 4, 14, 8, 0, tzinfo=UTC),
    )

    context = _make_service(db_session).get_specific_workout_context(workout.id)

    assert context.plan_summary is not None
    assert context.plan_summary.id == plan.id
    assert context.phase_summary is not None
    assert context.phase_summary.id == phase.id
    assert context.workout_status == "Done"
    assert context.workout_details.id == workout.id
    assert context.workout_details.tracked_sessions[0].id == tracked_session.id


def test_service_returns_sparse_context_for_workout_without_phase(
    db_session: Session,
) -> None:
    """The service supports standalone workouts that are not linked to a phase."""
    workout = create_workout(
        db_session,
        phase=None,
        name="Standalone Workout",
        status="Open",
        category="Mobility",
    )

    context = _make_service(db_session).get_specific_workout_context(workout.id)

    assert context.plan_summary is None
    assert context.phase_summary is None
    assert context.workout_status == "Open"
    assert context.workout_details.id == workout.id


def test_service_raises_for_missing_workout(db_session: Session) -> None:
    """The service raises a clear error when the workout does not exist."""
    with pytest.raises(ValueError, match="Workout not found"):
        _make_service(db_session).get_specific_workout_context(workout_id=999)
