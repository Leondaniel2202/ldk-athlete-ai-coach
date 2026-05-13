"""Event-related domain enums."""

from __future__ import annotations

from enum import StrEnum


class EventType(StrEnum):
    """Type of event represented in the training plan."""

    RACE = "Race"
    BENCHMARK = "Benchmark"
    SIMULATION = "Simulation"
    TRAINING_CAMP = "Training Camp"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> EventType:
        return cls.UNKNOWN


class EventPriority(StrEnum):
    """Priority of an event within the training plan."""

    A = "A"
    B = "B"
    C = "C"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> EventPriority:
        return cls.UNKNOWN


class EventStatus(StrEnum):
    """Lifecycle status captured for an event."""

    PLANNED = "Planned"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> EventStatus:
        return cls.UNKNOWN


class EventPlanRole(StrEnum):
    """Role an event plays inside a wider training plan."""

    PRIMARY = "Primary"
    SUPPORTING = "Supporting"
    C_TUNEUP = "Tune-up"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> EventPlanRole:
        return cls.UNKNOWN
