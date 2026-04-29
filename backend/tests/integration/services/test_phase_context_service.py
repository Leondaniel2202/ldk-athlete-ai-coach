"""Tests for the phase-context application service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session
from tests.factories.persisted_training_models import (
    create_phase,
    create_plan,
    create_tracked_session,
    create_workout,
)

from ldk_athlete_ai_coach.application.services.phase_context_service import PhaseContextService
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository

pytestmark = pytest.mark.integration


def _make_service(db: Session) -> PhaseContextService:
    return PhaseContextService(
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )


def test_service_returns_specific_phase_context_with_grouped_workouts(
    db_session: Session,
) -> None:
    """The service returns the requested phase with open and done workouts grouped."""
    now = datetime.now(tz=UTC)
    plan = create_plan(
        db_session,
        name="Build Plan",
        start_date_start=now - timedelta(days=14),
        end_date_start=now + timedelta(days=14),
    )
    phase = create_phase(
        db_session,
        name="Specific Build",
        plan=plan,
        timeframe_start=now - timedelta(days=7),
        timeframe_end=now + timedelta(days=7),
    )
    open_workout = create_workout(
        db_session,
        phase,
        name="Open Workout",
        date_start=now + timedelta(days=1),
        status="Open",
    )
    done_workout = create_workout(
        db_session,
        phase,
        name="Done Workout",
        date_start=now - timedelta(days=2),
        done_date_start=now - timedelta(days=1),
        status="Done",
    )
    create_tracked_session(
        db_session,
        done_workout,
        name="Completed Session",
        start=now - timedelta(hours=12),
    )

    context = _make_service(db_session).get_specific_phase_context(phase.id)

    assert context.plan_summary.id == plan.id
    assert context.phase.id == phase.id
    assert [workout.id for workout in context.open_workouts] == [open_workout.id]
    assert [workout.id for workout in context.done_workouts] == [done_workout.id]
    assert context.done_workouts[0].tracked_sessions[0].name == "Completed Session"
    assert context.adherence.planned_workouts == 2
    assert context.adherence.completed_workouts == 1
    assert context.adherence.skipped_workouts == 0
    assert context.adherence.unknown_workouts == 0
    assert context.data_gaps == []


def test_service_reports_unlinked_sessions_and_status_data_gaps(
    db_session: Session,
) -> None:
    """The service surfaces unlinked sessions and problematic workout statuses."""
    now = datetime.now(tz=UTC)
    plan = create_plan(
        db_session,
        name="Gap Plan",
        start_date_start=now - timedelta(days=14),
        end_date_start=now + timedelta(days=14),
    )
    phase = create_phase(
        db_session,
        name="Gap Phase",
        plan=plan,
        timeframe_start=now - timedelta(days=7),
        timeframe_end=now + timedelta(days=7),
    )
    create_workout(
        db_session,
        phase,
        name="Unknown Workout",
        date_start=now - timedelta(days=2),
        status="Unknown",
    )
    create_workout(
        db_session,
        phase,
        name="Missed Workout",
        date_start=now - timedelta(days=1),
        status="Missed",
    )
    create_tracked_session(
        db_session,
        None,
        name="Unlinked Session",
        start=now,
    )

    context = _make_service(db_session).get_specific_phase_context(phase.id)

    assert "1 session within the phase timeframe is not linked to any workout." in context.data_gaps
    assert "1 workout in this phase has an unknown status." in context.data_gaps
    assert "1 workout in this phase was missed." in context.data_gaps


def test_service_raises_for_missing_phase(db_session: Session) -> None:
    """The service raises a clear error when the phase does not exist."""
    with pytest.raises(ValueError, match="Phase not found"):
        _make_service(db_session).get_specific_phase_context(phase_id=999)
