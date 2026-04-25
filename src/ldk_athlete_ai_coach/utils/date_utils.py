"""Date and time utility helpers."""

from datetime import date, datetime, timedelta


def get_weeks_between_dates(start_date: datetime, end_date: datetime) -> int:
    """Calculate the number of weeks between two dates.

    Args:
        start_date: The starting date.
        end_date: The ending date.

    Returns:
        The number of weeks between the two dates, rounded up to the nearest whole week.
    """
    delta_days = (end_date - start_date).days
    return (delta_days // 7) + (1 if delta_days % 7 > 0 else 0)


def get_week_start_for_date(date: datetime) -> datetime:
    """Calculate the start date of the week for a given date.

    Assumes weeks start on the same day as the phase start date (e.g., Monday).

    Args:
        date: The date for which to calculate the week start.

    Returns:
        The start date of the week containing the given date.
    """
    return date - timedelta(days=date.weekday())


def get_week_end_for_date(date: datetime) -> datetime:
    """Calculate the end date of the week for a given date.

    Assumes weeks end on the same day as the phase start date (e.g., Sunday).

    Args:
        date: The date for which to calculate the week end.

    Returns:
        The end date of the week containing the given date.
    """
    return get_week_start_for_date(date) + timedelta(days=6)


def get_phase_week_number_for_date(phase_start_date: datetime, date: datetime) -> int:
    """Return the relative week number within a phase for a given date."""
    delta_days = (date - phase_start_date).days
    return (delta_days // 7) + 1


def coerce_to_date(value: datetime | date | None) -> date | None:
    """Coerce a datetime or date value to a date, or return None if the value is None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value
