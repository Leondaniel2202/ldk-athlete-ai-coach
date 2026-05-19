"""Event-related domain enums."""

from __future__ import annotations

from enum import StrEnum


class EventType(StrEnum):
    """Basic classification for an event."""

    RACE = "Race"
    COMPETITION = "Competition"
    BENCHMARK = "Benchmark"
    TRAINING_EVENT = "Training Event"
    OTHER = "Other"


class EventPriority(StrEnum):
    """Importance of an event in the training plan."""

    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    TUNE_UP = "Tune-up"
    LOW = "Low"


class EventStatus(StrEnum):
    """Lifecycle status for an event."""

    PLANNED = "Planned"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
