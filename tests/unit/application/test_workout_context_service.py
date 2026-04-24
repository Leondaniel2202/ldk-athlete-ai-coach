"""Unit tests for WorkoutContextService."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ldk_athlete_ai_coach.application.services.workout_context_service import WorkoutContextService
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus
from tests.unit.builders import make_phase, make_plan, make_workout

pytestmark = pytest.mark.unit


def test_get_specific_workout_context_raises_when_workout_missing() -> None:
    workout_repository = MagicMock()
    workout_repository.get_by_id.return_value = None
    service = WorkoutContextService(
        workout_repository=workout_repository,
        session_repository=MagicMock(),
    )

    with pytest.raises(ValueError, match="Workout not found"):
        service.get_specific_workout_context(workout_id=999)



def test_get_specific_workout_context_uses_unknown_status_when_workout_status_missing() -> None:
    workout = make_workout(
        workout_id=3,
        name="Compromised Run",
        status=None,
        phase=None,
    )
    workout_repository = MagicMock()
    workout_repository.get_by_id.return_value = workout
    service = WorkoutContextService(
        workout_repository=workout_repository,
        session_repository=MagicMock(),
    )

    context = service.get_specific_workout_context(workout_id=workout.id)

    assert context.plan_summary is None
    assert context.phase_summary is None
    assert context.workout_status == WorkoutStatus.UNKNOWN
    assert context.workout_details.id == workout.id



def test_get_specific_workout_context_includes_phase_and_plan_summaries() -> None:
    plan = make_plan()
    phase = make_phase(plan=plan)
    workout = make_workout(
        workout_id=3,
        name="Compromised Run",
        status=WorkoutStatus.DONE,
        phase=phase,
    )
    workout_repository = MagicMock()
    workout_repository.get_by_id.return_value = workout
    service = WorkoutContextService(
        workout_repository=workout_repository,
        session_repository=MagicMock(),
    )

    context = service.get_specific_workout_context(workout_id=workout.id)

    assert context.plan_summary is not None
    assert context.plan_summary.id == plan.id
    assert context.plan_summary.name == plan.name
    assert context.phase_summary is not None
    assert context.phase_summary.id == phase.id
    assert context.phase_summary.name == phase.name
    assert context.workout_status == WorkoutStatus.DONE
