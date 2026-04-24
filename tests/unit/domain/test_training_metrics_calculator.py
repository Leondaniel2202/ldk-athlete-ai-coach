"""Unit tests for the TrainingMetricsCalculator domain service."""

from __future__ import annotations

import pytest

from ldk_athlete_ai_coach.db.models.training import Workout
from ldk_athlete_ai_coach.domain.calculators.training_metrics_calculator import (
    TrainingMetricsCalculator,
)
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus

pytestmark = pytest.mark.unit


def _workout(
    *,
    name: str,
    status: WorkoutStatus,
    planned_training_load: float | None,
    actual_training_load: float | None,
) -> Workout:
    return Workout(
        notion_page_id=f"workout-{name}",
        notion_url=f"https://notion.so/workout-{name}",
        name=name,
        equipment=[],
        metrics_to_record=[],
        purpose=[],
        primarily_used_muscle_group=[],
        status=status,
        planned_training_load=planned_training_load,
        actual_training_load=actual_training_load,
        date_is_datetime=False,
        done_date_is_datetime=False,
        cancelled=False,
        skipped=False,
    )


def test_calculate_returns_expected_loads_and_adherence() -> None:
    calculator = TrainingMetricsCalculator()
    workouts = [
        _workout(
            name="done-1",
            status=WorkoutStatus.DONE,
            planned_training_load=100.0,
            actual_training_load=80.0,
        ),
        _workout(
            name="open-1",
            status=WorkoutStatus.OPEN,
            planned_training_load=200.0,
            actual_training_load=150.0,
        ),
    ]

    metrics = calculator.calculate(workouts)

    assert metrics.planned_training_load == 300.0
    assert metrics.actual_training_load == 230.0
    assert metrics.metric_adherence[0].metric_name == "Training Load Adherence"
    assert metrics.metric_adherence[0].adherence_percentage == pytest.approx(76.6666666667)
    assert metrics.included_statuses == {
        WorkoutStatus.DONE,
        WorkoutStatus.SKIPPED,
        WorkoutStatus.OPEN,
    }


def test_calculate_ignores_workouts_outside_included_statuses() -> None:
    calculator = TrainingMetricsCalculator()
    workouts = [
        _workout(
            name="done-1",
            status=WorkoutStatus.DONE,
            planned_training_load=100.0,
            actual_training_load=90.0,
        ),
        _workout(
            name="missed-1",
            status=WorkoutStatus.MISSED,
            planned_training_load=500.0,
            actual_training_load=500.0,
        ),
        _workout(
            name="cancelled-1",
            status=WorkoutStatus.CANCELLED,
            planned_training_load=500.0,
            actual_training_load=500.0,
        ),
    ]

    metrics = calculator.calculate(workouts)

    assert metrics.planned_training_load == 100.0
    assert metrics.actual_training_load == 90.0
    assert metrics.metric_adherence[0].adherence_percentage == 90.0


def test_calculate_ignores_none_load_values() -> None:
    calculator = TrainingMetricsCalculator()
    workouts = [
        _workout(
            name="done-none-planned",
            status=WorkoutStatus.DONE,
            planned_training_load=None,
            actual_training_load=60.0,
        ),
        _workout(
            name="open-none-actual",
            status=WorkoutStatus.OPEN,
            planned_training_load=120.0,
            actual_training_load=None,
        ),
    ]

    metrics = calculator.calculate(workouts)

    assert metrics.planned_training_load == 120.0
    assert metrics.actual_training_load == 60.0
    assert metrics.metric_adherence[0].adherence_percentage == 50.0


def test_calculate_returns_none_adherence_when_planned_load_is_zero() -> None:
    calculator = TrainingMetricsCalculator()
    workouts = [
        _workout(
            name="done-1",
            status=WorkoutStatus.DONE,
            planned_training_load=None,
            actual_training_load=10.0,
        ),
        _workout(
            name="open-1",
            status=WorkoutStatus.OPEN,
            planned_training_load=0.0,
            actual_training_load=5.0,
        ),
    ]

    metrics = calculator.calculate(workouts)

    assert metrics.planned_training_load == 0.0
    assert metrics.actual_training_load == 15.0
    assert metrics.metric_adherence[0].adherence_percentage is None


def test_calculate_with_empty_workouts_returns_zeros() -> None:
    calculator = TrainingMetricsCalculator()

    metrics = calculator.calculate([])

    assert metrics.planned_training_load == 0
    assert metrics.actual_training_load == 0
    assert metrics.metric_adherence[0].adherence_percentage is None
