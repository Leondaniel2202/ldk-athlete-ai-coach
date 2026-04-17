# domain/enums.py
from enum import Enum


class PlanStatus(str, Enum):  # noqa: UP042
    """The lifecycle status of a training plan, derived from the statuses of its phases."""

    ACTIVE = "Active"
    PAST = "Past"
    FUTURE = "Future"
    UNKNOWN = "Unknown"


class PhaseStatus(str, Enum):  # noqa: UP042
    """The lifecycle status of a training phase, derived from its timeframe and completion."""

    ACTIVE = "Active"
    PAST = "Past"
    FUTURE = "Future"
    UNKNOWN = "Unknown"


class WorkoutStatus(str, Enum):  # noqa: UP042
    """The lifecycle status of a workout, derived from its completion and adherence."""

    OPEN = "Open"
    DONE = "Done"
    MISSED = "Missed"
    SKIPPED = "Skipped"
    CANCELLED = "Cancelled"
    UNKNOWN = "Unknown"
