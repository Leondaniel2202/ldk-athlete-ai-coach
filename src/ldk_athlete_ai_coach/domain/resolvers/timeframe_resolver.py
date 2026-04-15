from datetime import datetime, timedelta


class TimeframeResolver:
    """Resolves planning timeframes based on phase structure."""

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
        today = today or datetime.utcnow()
        return self.get_week_number_for_date(phase_start_date, today)
