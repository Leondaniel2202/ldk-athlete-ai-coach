"""Workout-related domain enums and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WorkoutCategory(StrEnum):
    """Category of a workout."""

    RUN = "Run"
    STRENGTH = "Strength"
    HYROX = "HYROX"
    MOBILITY = "Mobility"
    CROSS_TRAINING = "Cross-training"
    BOXING = "Boxing"
    CONDITIONING = "Conditioning"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> WorkoutCategory:
        return cls.UNKNOWN


class WorkoutPurpose(StrEnum):
    """Purpose assigned to a planned workout."""

    AEROBIC = "Aerobic"
    SPEED = "Speed"
    RECOVERY = "Recovery"
    THRESHOLD = "Threshold"
    RACE_SPECIFIC = "Race-specific"
    STRENGTH = "Strength"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> WorkoutPurpose:
        return cls.UNKNOWN


class WorkoutEquipment(StrEnum):
    """Equipment required for a planned workout."""

    SHOES = "Shoes"
    HR_MONITOR = "HR Monitor"
    BIKE = "Bike"
    HELMET = "Helmet"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> WorkoutEquipment:
        return cls.UNKNOWN


class MuscleGroup(StrEnum):
    """Primary muscle group targeted by a workout."""

    LEGS = "Legs"
    FULL_BODY = "Full Body"
    CORE = "Core"
    UPPER_BODY = "Upper Body"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, _value: object) -> MuscleGroup:
        return cls.UNKNOWN


@dataclass(frozen=True)
class WorkoutCategoryDetails:
    """Human-readable details for a workout category."""

    label: str
    description: str


WORKOUT_CATEGORY_DETAILS: dict[WorkoutCategory, WorkoutCategoryDetails] = {
    WorkoutCategory.RUN: WorkoutCategoryDetails(
        label="Run",
        description=(
            "Aerobic running sessions ranging from easy recovery jogs to "
            "long runs and structured speed work. Forms the core of endurance training."
        ),
    ),
    WorkoutCategory.STRENGTH: WorkoutCategoryDetails(
        label="Strength",
        description=(
            "Resistance-based training focused on building muscular strength, "
            "power, and injury resilience to support overall athletic performance."
        ),
    ),
    WorkoutCategory.HYROX: WorkoutCategoryDetails(
        label="HYROX",
        description=(
            "Sport-specific preparation for HYROX competitions, combining functional "
            "fitness movements with running to simulate race demands."
        ),
    ),
    WorkoutCategory.MOBILITY: WorkoutCategoryDetails(
        label="Mobility",
        description=(
            "Flexibility and movement-quality work including stretching, yoga, and "
            "joint mobility drills to improve range of motion and aid recovery."
        ),
    ),
    WorkoutCategory.CROSS_TRAINING: WorkoutCategoryDetails(
        label="Cross-training",
        description=(
            "Low-impact aerobic activities such as cycling, swimming, or rowing "
            "used to maintain fitness while reducing running-specific stress."
        ),
    ),
    WorkoutCategory.BOXING: WorkoutCategoryDetails(
        label="Boxing",
        description=(
            "Boxing-based conditioning sessions that develop coordination, "
            "cardiovascular fitness, and upper-body power."
        ),
    ),
    WorkoutCategory.CONDITIONING: WorkoutCategoryDetails(
        label="Conditioning",
        description=(
            "High-intensity functional training sessions designed to improve "
            "overall work capacity, metabolic fitness, and athletic conditioning."
        ),
    ),
}


def get_workout_category_details(category: WorkoutCategory) -> WorkoutCategoryDetails:
    """Return details for a workout category."""
    return WORKOUT_CATEGORY_DETAILS[category]
