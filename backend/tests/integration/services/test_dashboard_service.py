"""Tests for the dashboard application service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session
from tests.factories.persisted_training_models import (
    create_phase,
    create_plan,
    create_workout,
)

from ldk_athlete_ai_coach.application.services.dashboard_service import DashboardService
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.plan_repository import PlanRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.utils.date_utils import get_week_start_for_date

pytestmark = pytest.mark.integration


def _make_service(db: Session) -> DashboardService:
    return DashboardService(
        plan_repository=PlanRepository(db),
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )


def test_service_returns_dashboard_for_current_training_week(db_session: Session) -> None:
    """The service aggregates active context and current-week workouts."""
    now = datetime.now(tz=UTC)
    week_start = get_week_start_for_date(now).replace(hour=0, minute=0, second=0, microsecond=0)
    plan = create_plan(
        db_session,
        name="Active Dashboard Plan",
        start_date_start=now - timedelta(days=14),
        end_date_start=now + timedelta(days=14),
    )
    phase = create_phase(
        db_session,
        name="Active Dashboard Phase",
        plan=plan,
        phase_type="Build",
        timeframe_start=now - timedelta(days=7),
        timeframe_end=now + timedelta(days=7),
    )
    done_workout = create_workout(
        db_session,
        phase,
        name="Done Dashboard Run",
        status="Done",
        category="Run",
        planned_week_start_date=week_start,
        planned_training_load=100.0,
    )
    skipped_workout = create_workout(
        db_session,
        phase,
        name="Skipped Dashboard Strength",
        status="Skipped",
        category="Strength",
        planned_week_start_date=week_start,
        planned_training_load=50.0,
    )
    create_workout(
        db_session,
        phase,
        name="Future Dashboard Run",
        status="Open",
        category="Run",
        planned_week_start_date=week_start + timedelta(days=7),
    )

    dashboard = _make_service(db_session).get_dashboard()

    assert dashboard.current_plan is not None
    assert dashboard.current_plan.id == plan.id
    assert dashboard.current_phase is not None
    assert dashboard.current_phase.id == phase.id
    assert [workout.id for workout in dashboard.weekly_outlook] == [
        skipped_workout.id,
        done_workout.id,
    ]
    assert dashboard.overview[0].value == "Build"
    assert dashboard.overview[1].value == "2 Workouts"
    assert dashboard.overview[1].detail == "1 Run workout, 1 Strength workout"
    assert dashboard.overview[2].value == "Needs Attention"
    assert dashboard.overview[2].detail == "1 done, 1 skipped, 0 open"
    assert dashboard.overview[3].value == "150.0"


def test_service_returns_sparse_dashboard_when_no_current_training_context(
    db_session: Session,
) -> None:
    """The service returns a usable dashboard when no active records exist."""
    dashboard = _make_service(db_session).get_dashboard()

    assert dashboard.current_plan is None
    assert dashboard.current_phase is None
    assert dashboard.weekly_outlook == []
    assert dashboard.overview[0].value is None
    assert dashboard.overview[1].value == "0 Workouts"
    assert dashboard.overview[2].detail == "0 done, 0 skipped, 0 open"
