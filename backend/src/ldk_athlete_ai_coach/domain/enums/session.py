"""Tracked-session-related domain enums."""

from __future__ import annotations

from enum import StrEnum


class SessionSource(StrEnum):
    """System that produced a tracked session."""

    APPLE_HEALTH = "Apple Health"
    GARMIN = "Garmin"
    STRAVA = "Strava"
    MANUAL = "Manual"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> SessionSource:
        return cls.UNKNOWN


class SessionType(StrEnum):
    """Concrete activity type recorded in a tracked session."""

    RUNNING = "Running"
    CYCLING = "Cycling"
    STRENGTH = "Strength"
    HYROX = "HYROX"
    MOBILITY = "Mobility"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> SessionType:
        return cls.UNKNOWN
