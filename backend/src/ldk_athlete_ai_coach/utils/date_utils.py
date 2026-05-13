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


def get_phase_week_number_for_date(phase_start_date: date | datetime, date: date | datetime) -> int:
    """Return the relative week number within a phase for a given date.

    Week 1 begins on ``phase_start_date``. Each subsequent week starts every
    7 days after that.

    Args:
        phase_start_date: The first day of the phase.
        date: The date for which to determine the week number.

    Returns:
        A 1-based week number relative to the phase start.
    """
    phase_start = coerce_to_date(phase_start_date)
    current = coerce_to_date(date)
    if phase_start is None or current is None:
        raise ValueError("phase_start_date and date must both be defined")
    delta_days = (current - phase_start).days
    return (delta_days // 7) + 1


def get_date_for_phase_week_number(phase_start_date: datetime, week_number: int) -> datetime:
    """Return the start date of the given week number within a phase.

    This is the inverse of :func:`get_phase_week_number_for_date`. Week 1
    returns ``phase_start_date`` unchanged.

    Args:
        phase_start_date: The first day of the phase.
        week_number: A 1-based week number relative to the phase start.

    Returns:
        The datetime at the start of the given week within the phase.
    """
    return phase_start_date + timedelta(weeks=week_number - 1)


def coerce_to_date(value: datetime | date | None) -> date | None:
    """Coerce a datetime or date value to a plain date.

    Args:
        value: A :class:`datetime`, :class:`date`, or ``None``.

    Returns:
        The date portion of the value, or ``None`` if the input is ``None``.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value
