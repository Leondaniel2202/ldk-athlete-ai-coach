from __future__ import annotations

from datetime import date, datetime

from ldk_athlete_ai_coach.domain.calculators.status_calculator import (
    StatusCalculator,
    WorkoutStatusContext,
)
from ldk_athlete_ai_coach.domain.enums.status import PhaseStatus, WorkoutStatus


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
