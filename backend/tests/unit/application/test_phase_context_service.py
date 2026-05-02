"""Unit tests for PhaseContextService."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from tests.factories.in_memory_training_models import (
    build_phase,
    build_plan,
    build_session,
    build_workout,
)

from ldk_athlete_ai_coach.application.services.phase_context_service import PhaseContextService
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus

pytestmark = pytest.mark.unit


def _service() -> tuple[PhaseContextService, MagicMock, MagicMock, MagicMock]:
    phase_repository = MagicMock()
    workout_repository = MagicMock()
    session_repository = MagicMock()
    service = PhaseContextService(
        phase_repository=phase_repository,
        workout_repository=workout_repository,
        session_repository=session_repository,
    )
    return service, phase_repository, workout_repository, session_repository


def test_get_specific_phase_context_groups_workouts_and_builds_weekly_metrics() -> None:
    service, phase_repository, workout_repository, session_repository = _service()
    now = datetime.now(tz=UTC)
    plan = build_plan()
    phase = build_phase(
        plan=plan,
        timeframe_start=now - timedelta(days=7),
        timeframe_end=now + timedelta(days=7),
    )
    week_1 = datetime(2026, 4, 7, tzinfo=UTC)
    week_2 = datetime(2026, 4, 14, tzinfo=UTC)
    done_workout = build_workout(
        workout_id=10,
        name="Done Workout",
        status=WorkoutStatus.DONE,
        phase=phase,
        planned_week_start_date=week_1,
    )
    open_workout = build_workout(
        workout_id=11,
        name="Open Workout",
        status=WorkoutStatus.OPEN,
        phase=phase,
        planned_week_start_date=week_2,
    )

    phase_repository.get_by_id.return_value = phase
    workout_repository.list_by_phase_id.return_value = [done_workout, open_workout]
    session_repository.list_by_workout_ids.return_value = [
        build_session(session_id=99, workout_id=10)
    ]
    session_repository.list_unlinked_within_window.return_value = []

    context = service.get_specific_phase_context(phase_id=phase.id)

    assert context.phase.id == phase.id
    assert context.plan_summary.id == plan.id
    assert [workout.id for workout in context.open_workouts] == [open_workout.id]
    assert [workout.id for workout in context.done_workouts] == [done_workout.id]
    assert len(context.done_workouts[0].tracked_sessions) == 1
    assert len(context.weekly_metrics) == 2
    assert context.adherence.planned_workouts == 2
    assert context.adherence.completed_workouts == 1
    assert context.adherence.completion_ratio == 0.5
    assert context.data_gaps == []


def test_get_specific_phase_context_reports_unknown_phase_timeframe_gap() -> None:
    service, phase_repository, workout_repository, session_repository = _service()
    plan = build_plan()
    phase = build_phase(plan=plan, timeframe_start=None, timeframe_end=None)
    workout = build_workout(
        workout_id=12,
        name="Unknown Workout",
        status=WorkoutStatus.UNKNOWN,
        phase=phase,
        planned_week_start_date=None,
    )

    phase_repository.get_by_id.return_value = phase
    workout_repository.list_by_phase_id.return_value = [workout]
    session_repository.list_by_workout_ids.return_value = []

    context = service.get_specific_phase_context(phase_id=phase.id)

    assert len(context.weekly_metrics) == 1
    assert (
        "Phase timeframe is not fully defined; unable to determine phase status."
        in context.data_gaps
    )
    assert "1 workout in this phase has an unknown status." in context.data_gaps
    session_repository.list_unlinked_within_window.assert_not_called()


def test_get_specific_phase_week_context_builds_week_metadata_and_data_gaps() -> None:
    service, phase_repository, workout_repository, session_repository = _service()
    now = datetime.now(tz=UTC)
    plan = build_plan()
    phase_start = datetime(2026, 4, 7, tzinfo=UTC)
    phase = build_phase(
        plan=plan,
        timeframe_start=phase_start,
        timeframe_end=now + timedelta(days=7),
    )
    week_start = datetime(2026, 4, 14, tzinfo=UTC)
    week_workout = build_workout(
        workout_id=13,
        name="Missed Workout",
        status=WorkoutStatus.MISSED,
        phase=phase,
        planned_week_start_date=week_start,
    )

    phase_repository.get_by_id.return_value = phase
    workout_repository.list_within_planned_week.return_value = [week_workout]
    session_repository.list_unlinked_within_window.return_value = [
        build_session(session_id=100, workout_id=None)
    ]

    phase_repository.get_by_date.return_value = phase

    context = service.get_specific_phase_week_context(week_start_date=week_start)

    assert context.plan_summary.id == plan.id
    assert context.phase_summary.id == phase.id
    assert context.metadata.phase_week_number == 2
    assert context.metadata.phase_week_start_date == week_start
    assert len(context.workouts) == 1
    assert context.adherence.planned_workouts == 1
    assert "1 workout in this phase week was missed." in context.data_gaps
    assert "1 session within the phase timeframe is not linked to any workout." in context.data_gaps


def test_get_specific_phase_week_context_raises_when_phase_missing() -> None:
    service, phase_repository, _, _ = _service()
    phase_repository.get_by_date.return_value = None

    with pytest.raises(ValueError, match="No phase found for the given week start date"):
        service.get_specific_phase_week_context(
            week_start_date=datetime(2026, 4, 14, tzinfo=UTC),
        )
