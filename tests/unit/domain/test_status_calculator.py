"""Unit tests for the StatusCalculator domain service."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from ldk_athlete_ai_coach.domain.calculators.status_calculator import (
    StatusCalculator,
    WorkoutStatusContext,
)
from ldk_athlete_ai_coach.domain.enums.status import PhaseStatus, PlanStatus, WorkoutStatus

pytestmark = pytest.mark.unit


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


def test_calculate_phase_status_future() -> None:
    calculator = StatusCalculator()

    status = calculator.calculate_phase_status(
        timeframe_start=date(2026, 5, 1),
        timeframe_end=date(2026, 5, 31),
        as_of_date=date(2026, 4, 17),
    )

    assert status == PhaseStatus.FUTURE


def test_calculate_phase_status_past() -> None:
    calculator = StatusCalculator()

    status = calculator.calculate_phase_status(
        timeframe_start=date(2026, 1, 1),
        timeframe_end=date(2026, 2, 28),
        as_of_date=date(2026, 4, 17),
    )

    assert status == PhaseStatus.PAST


def test_calculate_plan_status_future() -> None:
    calculator = StatusCalculator()

    status = calculator.calculate_plan_status(
        timeframe_start=date(2026, 5, 1),
        timeframe_end=date(2026, 5, 31),
        as_of_date=date(2026, 4, 17),
    )

    assert status == PlanStatus.FUTURE


def test_calculate_plan_status_active() -> None:
    calculator = StatusCalculator()

    status = calculator.calculate_plan_status(
        timeframe_start=date(2026, 4, 1),
        timeframe_end=date(2026, 4, 30),
        as_of_date=date(2026, 4, 17),
    )

    assert status == PlanStatus.ACTIVE


def test_calculate_plan_status_past() -> None:
    calculator = StatusCalculator()

    status = calculator.calculate_plan_status(
        timeframe_start=date(2026, 1, 1),
        timeframe_end=date(2026, 2, 28),
        as_of_date=date(2026, 4, 17),
    )

    assert status == PlanStatus.PAST


def test_calculate_plan_status_active_when_no_boundaries() -> None:
    calculator = StatusCalculator()

    status = calculator.calculate_plan_status(
        timeframe_start=None,
        timeframe_end=None,
        as_of_date=date(2026, 4, 17),
    )

    assert status == PlanStatus.UNKNOWN


def test_calculate_phase_status_unknown_when_no_boundaries() -> None:
    calculator = StatusCalculator()

    status = calculator.calculate_phase_status(
        timeframe_start=None,
        timeframe_end=None,
        as_of_date=date(2026, 4, 17),
    )

    assert status == PhaseStatus.UNKNOWN


def test_calculate_phase_status_unknown_when_timeframe_is_incomplete() -> None:
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

    assert status_without_start == PhaseStatus.UNKNOWN
    assert status_without_end == PhaseStatus.UNKNOWN


def test_calculate_plan_status_unknown_when_timeframe_is_incomplete() -> None:
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

    assert status_without_start == PlanStatus.UNKNOWN
    assert status_without_end == PlanStatus.UNKNOWN


def test_calculate_workout_status_cancelled_takes_priority() -> None:
    calculator = StatusCalculator()
    context = WorkoutStatusContext(
        is_cancelled=True,
        is_skipped=True,
        session_count=1,
        actual_rpe=8.0,
        phase_status=PhaseStatus.ACTIVE,
        timeframe_start=None,
        timeframe_end=None,
    )

    status = calculator.calculate_workout_status(context, as_of_date=date(2026, 4, 17))

    assert status == WorkoutStatus.CANCELLED


def test_calculate_workout_status_skipped() -> None:
    calculator = StatusCalculator()
    context = WorkoutStatusContext(
        is_cancelled=False,
        is_skipped=True,
        session_count=0,
        actual_rpe=None,
        phase_status=PhaseStatus.ACTIVE,
        timeframe_start=None,
        timeframe_end=None,
    )

    status = calculator.calculate_workout_status(context, as_of_date=date(2026, 4, 17))

    assert status == WorkoutStatus.SKIPPED


def test_calculate_workout_status_done_when_session_and_rpe() -> None:
    calculator = StatusCalculator()
    context = WorkoutStatusContext(
        is_cancelled=False,
        is_skipped=False,
        session_count=1,
        actual_rpe=7.5,
        phase_status=PhaseStatus.ACTIVE,
        timeframe_start=date(2026, 4, 15),
        timeframe_end=date(2026, 4, 15),
    )

    status = calculator.calculate_workout_status(context, as_of_date=date(2026, 4, 17))

    assert status == WorkoutStatus.DONE


def test_calculate_workout_status_missed_when_phase_past() -> None:
    calculator = StatusCalculator()
    context = WorkoutStatusContext(
        is_cancelled=False,
        is_skipped=False,
        session_count=0,
        actual_rpe=None,
        phase_status=PhaseStatus.PAST,
        timeframe_start=None,
        timeframe_end=None,
    )

    status = calculator.calculate_workout_status(context, as_of_date=date(2026, 4, 17))

    assert status == WorkoutStatus.MISSED


def test_calculate_workout_status_open_when_timeframe_is_in_future() -> None:
    calculator = StatusCalculator()
    context = WorkoutStatusContext(
        is_cancelled=False,
        is_skipped=False,
        session_count=0,
        actual_rpe=None,
        phase_status=None,
        timeframe_start=date(2026, 4, 20),
        timeframe_end=date(2026, 4, 20),
    )

    status = calculator.calculate_workout_status(context, as_of_date=date(2026, 4, 17))

    assert status == WorkoutStatus.OPEN


def test_calculate_workout_status_missed_when_timeframe_is_in_past() -> None:
    calculator = StatusCalculator()
    context = WorkoutStatusContext(
        is_cancelled=False,
        is_skipped=False,
        session_count=0,
        actual_rpe=None,
        phase_status=None,
        timeframe_start=date(2026, 4, 10),
        timeframe_end=date(2026, 4, 12),
    )

    status = calculator.calculate_workout_status(context, as_of_date=date(2026, 4, 17))

    assert status == WorkoutStatus.MISSED


def test_calculate_workout_status_unknown_without_phase_or_timeframe_signal() -> None:
    calculator = StatusCalculator()
    context = WorkoutStatusContext(
        is_cancelled=False,
        is_skipped=False,
        session_count=0,
        actual_rpe=None,
        phase_status=None,
        timeframe_start=None,
        timeframe_end=None,
    )

    status = calculator.calculate_workout_status(context, as_of_date=date(2026, 4, 17))

    assert status == WorkoutStatus.UNKNOWN
