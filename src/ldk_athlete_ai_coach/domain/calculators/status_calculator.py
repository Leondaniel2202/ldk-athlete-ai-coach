"""Status calculation utilities for training plans, phases, and workouts.

This module centralizes the lifecycle and completion-state decision logic used by
domain services to derive statuses from temporal boundaries and workout context.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from ldk_athlete_ai_coach.domain.enums.status import PhaseStatus, PlanStatus, WorkoutStatus


class TemporalStatus(StrEnum):
    """Represents a generic temporal state relative to a reference date.

    Values:
        FUTURE: The entity starts after the reference date.
        PAST: The entity ended before the reference date.
        ACTIVE: The reference date falls within the entity timeframe.
        UNKNOWN: The timeframe data is insufficient or inconsistent.
    """

    FUTURE = "Future"
    PAST = "Past"
    ACTIVE = "Active"
    UNKNOWN = "Unknown"


@dataclass(slots=True)
class WorkoutStatusContext:
    """Input payload used to determine a workout's status.

    Attributes:
        is_cancelled: Whether the workout was explicitly cancelled.
        is_skipped: Whether the workout was explicitly skipped.
        session_count: Number of recorded sessions for the workout.
        actual_rpe: Actual perceived exertion recorded for the workout.
        phase_status: Resolved status of the parent training phase.
        timeframe_start: Scheduled start date for the workout timeframe.
        timeframe_end: Scheduled end date for the workout timeframe.
    """

    is_cancelled: bool
    is_skipped: bool
    session_count: int
    actual_rpe: float | None
    phase_status: PhaseStatus | None
    timeframe_start: date | None
    timeframe_end: date | None


class StatusCalculator:
    """Calculate lifecycle statuses for training entities."""

    def _calculate_temporal_status(
        self,
        *,
        timeframe_start: date | None,
        timeframe_end: date | None,
        as_of_date: date,
    ) -> TemporalStatus:
        """Calculate a generic temporal status from timeframe boundaries.

        Args:
            timeframe_start: Optional start date of the timeframe.
            timeframe_end: Optional end date of the timeframe.
            as_of_date: Reference date used for status evaluation.

        Returns:
            TemporalStatus: Derived temporal state relative to ``as_of_date``.
        """

        if timeframe_start is not None and timeframe_start > as_of_date:
            return TemporalStatus.FUTURE

        if timeframe_end is not None and timeframe_end < as_of_date:
            return TemporalStatus.PAST

        if (timeframe_start is None or timeframe_start <= as_of_date) and (
            timeframe_end is None or timeframe_end >= as_of_date
        ):
            return TemporalStatus.ACTIVE

        return TemporalStatus.UNKNOWN

    def calculate_phase_status(
        self,
        *,
        timeframe_start: date | None,
        timeframe_end: date | None,
        as_of_date: date,
    ) -> PhaseStatus:
        """Calculate the status of a training phase.

        Args:
            timeframe_start: Optional start date of the phase.
            timeframe_end: Optional end date of the phase.
            as_of_date: Reference date used to evaluate phase status.

        Returns:
            PhaseStatus: Calculated phase lifecycle status.
        """

        return PhaseStatus(
            self._calculate_temporal_status(
                timeframe_start=timeframe_start,
                timeframe_end=timeframe_end,
                as_of_date=as_of_date,
            )
        )

    def calculate_plan_status(
        self,
        *,
        timeframe_start: date | None,
        timeframe_end: date | None,
        as_of_date: date,
    ) -> PlanStatus:
        """Calculate the status of a training plan.

        Args:
            timeframe_start: Optional start date of the plan.
            timeframe_end: Optional end date of the plan.
            as_of_date: Reference date used to evaluate plan status.

        Returns:
            PlanStatus: Calculated plan lifecycle status.
        """

        return PlanStatus(
            self._calculate_temporal_status(
                timeframe_start=timeframe_start,
                timeframe_end=timeframe_end,
                as_of_date=as_of_date,
            )
        )

    def calculate_workout_status(
        self,
        context: WorkoutStatusContext,
        *,
        as_of_date: date,
    ) -> WorkoutStatus:
        """Calculate the status of an individual workout.

        Decision precedence is:
            1. Cancelled
            2. Skipped
            3. Done (session and non-zero RPE recorded)
            4. Missed (past phase or past workout timeframe)
            5. Open (future/active phase or future workout timeframe)
            6. Unknown

        Args:
            context: Collected workout and scheduling attributes.
            as_of_date: Reference date used to resolve temporal conditions.

        Returns:
            WorkoutStatus: Calculated workout status.
        """

        has_sessions = context.session_count > 0
        has_actual_rpe = context.actual_rpe is not None and context.actual_rpe != 0

        timeframe_in_future = (
            context.timeframe_start is not None and context.timeframe_start > as_of_date
        )
        timeframe_in_past = context.timeframe_end is not None and context.timeframe_end < as_of_date

        if context.is_cancelled:
            return WorkoutStatus.CANCELLED

        if context.is_skipped:
            return WorkoutStatus.SKIPPED

        if has_sessions and has_actual_rpe:
            return WorkoutStatus.DONE

        if context.phase_status == PhaseStatus.PAST:
            return WorkoutStatus.MISSED

        if timeframe_in_past:
            return WorkoutStatus.MISSED

        if context.phase_status in {PhaseStatus.FUTURE, PhaseStatus.ACTIVE}:
            return WorkoutStatus.OPEN

        if timeframe_in_future:
            return WorkoutStatus.OPEN

        return WorkoutStatus.UNKNOWN
