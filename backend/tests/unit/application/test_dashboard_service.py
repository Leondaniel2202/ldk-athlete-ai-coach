"""Unit tests for DashboardService."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from tests.factories.in_memory_training_models import (
    build_phase,
    build_plan,
    build_workout,
)

from ldk_athlete_ai_coach.application.services.dashboard_service import DashboardService
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus

pytestmark = pytest.mark.unit


def _service() -> tuple[DashboardService, MagicMock, MagicMock, MagicMock, MagicMock]:
    plan_repository = MagicMock()
    phase_repository = MagicMock()
    workout_repository = MagicMock()
    session_repository = MagicMock()
    service = DashboardService(
        plan_repository=plan_repository,
        phase_repository=phase_repository,
        workout_repository=workout_repository,
        session_repository=session_repository,
    )
    return service, plan_repository, phase_repository, workout_repository, session_repository


def test_get_dashboard_builds_current_training_overview() -> None:
    service, plan_repository, phase_repository, workout_repository, _ = _service()
    plan = build_plan(name="Current Plan")
    phase = build_phase(plan=plan)
    done_workout = build_workout(
        workout_id=10,
        name="Done Run",
        status=WorkoutStatus.DONE,
        phase=phase,
        planned_training_load=125.0,
    )
    open_workout = build_workout(
        workout_id=11,
        name="Open Run",
        status=WorkoutStatus.OPEN,
        phase=phase,
        planned_training_load=75.0,
    )
    plan_repository.get_active_for_datetime.return_value = plan
    phase_repository.get_active_for_datetime.return_value = phase
    workout_repository.list_within_planned_week.return_value = [done_workout, open_workout]

    dashboard = service.get_dashboard()

    assert dashboard.current_plan is not None
    assert dashboard.current_plan.id == plan.id
    assert dashboard.current_phase is not None
    assert dashboard.current_phase.id == phase.id
    assert [workout.id for workout in dashboard.weekly_outlook] == [
        done_workout.id,
        open_workout.id,
    ]
    assert [item.label for item in dashboard.overview] == [
        "Training focus",
        "This Week",
        "Execution",
        "Planned Training Load",
    ]
    assert dashboard.overview[0].value == "Build"
    assert dashboard.overview[1].value == "2 Workouts"
    assert dashboard.overview[1].detail == "2 Run workouts"
    assert dashboard.overview[2].value == "On Track"
    assert dashboard.overview[2].detail == "1 done, 0 skipped, 1 open"
    assert dashboard.overview[3].value == "200.0"
    workout_repository.list_within_planned_week.assert_called_once()


def test_get_dashboard_marks_execution_as_needing_attention_when_workout_skipped() -> None:
    service, plan_repository, phase_repository, workout_repository, _ = _service()
    plan = build_plan()
    phase = build_phase(plan=plan)
    skipped_workout = build_workout(
        workout_id=12,
        name="Skipped Run",
        status=WorkoutStatus.SKIPPED,
        phase=phase,
    )
    plan_repository.get_active_for_datetime.return_value = plan
    phase_repository.get_active_for_datetime.return_value = phase
    workout_repository.list_within_planned_week.return_value = [skipped_workout]

    dashboard = service.get_dashboard()

    assert dashboard.overview[2].value == "Needs Attention"
    assert dashboard.overview[2].detail == "0 done, 1 skipped, 0 open"


def test_get_dashboard_returns_sparse_overview_without_current_plan_or_phase() -> None:
    service, plan_repository, phase_repository, workout_repository, _ = _service()
    plan_repository.get_active_for_datetime.return_value = None
    phase_repository.get_active_for_datetime.return_value = None
    workout_repository.list_within_planned_week.return_value = []

    dashboard = service.get_dashboard()

    assert dashboard.current_plan is None
    assert dashboard.current_phase is None
    assert dashboard.weekly_outlook == []
    assert dashboard.overview[0].value is None
    assert dashboard.overview[0].detail is None
    assert dashboard.overview[1].value == "0 Workouts"
    assert dashboard.overview[1].detail == ""
    assert dashboard.overview[2].value == "On Track"
    assert dashboard.overview[3].value == "0"
