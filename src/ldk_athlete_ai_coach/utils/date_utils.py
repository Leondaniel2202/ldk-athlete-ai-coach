from datetime import datetime, timedelta


def get_week_timeframe_by_week_number(
    year: int = datetime.now().year, week_number: int = datetime.now().isocalendar()[1]
) -> tuple[datetime, datetime]:
    """Calculate the start and end datetimes for a given ISO week of a year.

    Args:
        year: The calendar year for the desired week.
        week_number: The ISO week number (1-53).

    Returns:
        A tuple containing the start and end datetimes of the specified week.
    """
    first_day_of_year = datetime(year=year, month=1, day=4)
    start_of_week = first_day_of_year + timedelta(
        weeks=week_number - 1, days=-first_day_of_year.weekday()
    )
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def get_week_number_for_date(date: datetime) -> int:
    """Calculate the ISO week number for a given date.

    Args:
        date: The date for which to calculate the week number.
    Returns:
        The ISO week number (1-53) corresponding to the given date.
    """
    return date.isocalendar()[1]


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
