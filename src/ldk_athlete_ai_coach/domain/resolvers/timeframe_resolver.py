from datetime import UTC, datetime, timedelta

from ldk_athlete_ai_coach.domain.enums.status import TimeframeStatus


class TimeframeResolver:
    """Utility class for resolving timeframe-related information such as week numbers,
    start/end dates, and status. This is used to determine the current training context
    and to classify timeframes as past, current, or future."""

    def get_week_timeframe(
        self, phase_start_date: datetime, week_number: int
    ) -> tuple[datetime, datetime]:
        """
        Returns the start and end date for a given week in a phase.

        Week 1 starts at phase_start_date.
        """
        start = phase_start_date + timedelta(weeks=week_number - 1)
        end = start + timedelta(days=6)
        return start, end

    def get_week_number_for_date(self, phase_start_date: datetime, date: datetime) -> int:
        """
        Returns the relative week number within a phase for a given date.
        """
        delta_days = (date - phase_start_date).days
        return (delta_days // 7) + 1

    def get_current_week(self, phase_start_date: datetime, today: datetime | None = None) -> int:
        """
        Returns the current week number within a phase.
        """
        today = today or datetime.now(tz=UTC)
        return self.get_week_number_for_date(phase_start_date, today)

    def get_weeks_between_dates(self, start_date: datetime, end_date: datetime) -> int:
        """
        Returns the number of weeks between two dates.
        """
        delta_days = (end_date - start_date).days
        return (delta_days // 7) + 1

    def get_week_start_for_date(self, date: datetime) -> datetime:
        """
        Returns the start date of the week for a given date.
        Assumes weeks start on the same day as the phase start date (e.g., Monday).
        """
        return date - timedelta(days=date.weekday())

    def get_week_end_for_date(self, date: datetime) -> datetime:
        """Returns the end date of the week for a given date.
        Assumes weeks end on the same day as the phase start date (e.g., Sunday).
        """
        return self.get_week_start_for_date(date) + timedelta(days=6)

    def get_timeframe_status(
        self, start_date: datetime, end_date: datetime, as_of: datetime | None = None
    ) -> TimeframeStatus:
        """
        Determines if a given timeframe is in the past, current, or future relative to 'as_of' date.
        """
        as_of = as_of or datetime.now(tz=UTC)
        if as_of < start_date:
            return TimeframeStatus.FUTURE
        if as_of > end_date:
            return TimeframeStatus.PAST
        return TimeframeStatus.CURRENT
