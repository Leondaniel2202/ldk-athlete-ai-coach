from __future__ import annotations

from datetime import date, datetime

from ldk_athlete_ai_coach.domain.calculators.status_calculator import (
    StatusCalculator,
    WorkoutStatusContext,
)
from ldk_athlete_ai_coach.domain.enums.status import PhaseStatus, PlanStatus, WorkoutStatus


def test_calculate_phase_status_accepts_datetime_boundaries() -> None:
    calculator = StatusCalculator()

    status = calculator.calculate_phase_status(
        timeframe_start=datetime(2026, 4, 1, 9, 0),
        timeframe_end=datetime(2026, 4, 30, 18, 0),
        as_of_date=date(2026, 4, 17),
    )

    assert status == PhaseStatus.ACTIVE


def test_calculate_workout_status_accepts_datetime_boundaries() -> None:
    calculator = StatusCalculator()
    context = WorkoutStatusContext(
        is_cancelled=False,
        is_skipped=False,
        session_count=0,
        actual_rpe=None,
        phase_status=PhaseStatus.ACTIVE,
        timeframe_start=datetime(2026, 4, 18, 6, 0),
        timeframe_end=datetime(2026, 4, 18, 7, 0),
    )

    status = calculator.calculate_workout_status(context, as_of_date=date(2026, 4, 17))

    assert status == WorkoutStatus.OPEN


def test_calculate_phase_status_returns_unknown_when_timeframe_is_incomplete() -> None:
    calculator = StatusCalculator()

    status_without_start = calculator.calculate_phase_status(
        timeframe_start=None,
        timeframe_end=date(2026, 4, 30),
        as_of_date=date(2026, 4, 17),
    )
    status_without_end = calculator.calculate_phase_status(
        timeframe_start=date(2026, 4, 1),
        timeframe_end=None,
        as_of_date=date(2026, 4, 17),
    )
    status_without_bounds = calculator.calculate_phase_status(
        timeframe_start=None,
        timeframe_end=None,
        as_of_date=date(2026, 4, 17),
    )

    assert status_without_start == PhaseStatus.UNKNOWN
    assert status_without_end == PhaseStatus.UNKNOWN
    assert status_without_bounds == PhaseStatus.UNKNOWN


def test_calculate_plan_status_returns_unknown_when_timeframe_is_incomplete() -> None:
    calculator = StatusCalculator()

    status_without_start = calculator.calculate_plan_status(
        timeframe_start=None,
        timeframe_end=date(2026, 4, 30),
        as_of_date=date(2026, 4, 17),
    )
    status_without_end = calculator.calculate_plan_status(
        timeframe_start=date(2026, 4, 1),
        timeframe_end=None,
        as_of_date=date(2026, 4, 17),
    )
    status_without_bounds = calculator.calculate_plan_status(
        timeframe_start=None,
        timeframe_end=None,
        as_of_date=date(2026, 4, 17),
    )

    assert status_without_start == PlanStatus.UNKNOWN
    assert status_without_end == PlanStatus.UNKNOWN
    assert status_without_bounds == PlanStatus.UNKNOWN
