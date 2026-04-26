"""Unit tests for date utility helpers."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from ldk_athlete_ai_coach.utils.date_utils import (
    coerce_to_date,
    get_phase_week_number_for_date,
    get_week_end_for_date,
    get_week_start_for_date,
    get_weeks_between_dates,
)

pytestmark = pytest.mark.unit


def test_get_weeks_between_dates_rounds_up_partial_week() -> None:
    start = datetime(2026, 4, 1)
    end = datetime(2026, 4, 10)

    weeks = get_weeks_between_dates(start, end)

    assert weeks == 2


def test_get_weeks_between_dates_exact_week_boundary() -> None:
    start = datetime(2026, 4, 1)
    end = datetime(2026, 4, 8)

    weeks = get_weeks_between_dates(start, end)

    assert weeks == 1


def test_get_week_start_for_date_returns_monday() -> None:
    value = datetime(2026, 4, 24)  # Friday

    week_start = get_week_start_for_date(value)

    assert week_start == datetime(2026, 4, 20)


def test_get_week_end_for_date_returns_sunday() -> None:
    value = datetime(2026, 4, 24)  # Friday

    week_end = get_week_end_for_date(value)

    assert week_end == datetime(2026, 4, 26)


def test_get_phase_week_number_for_date_is_one_based() -> None:
    phase_start = datetime(2026, 4, 1)

    assert get_phase_week_number_for_date(phase_start, datetime(2026, 4, 1)) == 1
    assert get_phase_week_number_for_date(phase_start, datetime(2026, 4, 7)) == 1
    assert get_phase_week_number_for_date(phase_start, datetime(2026, 4, 8)) == 2


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        (date(2026, 4, 24), date(2026, 4, 24)),
        (datetime(2026, 4, 24, 12, 30), date(2026, 4, 24)),
    ],
)
def test_coerce_to_date(value: datetime | date | None, expected: date | None) -> None:
    assert coerce_to_date(value) == expected
