"""Phase-related domain enums and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PhaseType(StrEnum):
    """Type of a training phase."""

    BASE = "Base"
    BUILD = "Build"
    PEAK = "Peak"
    TAPER = "Taper"
    RECOVERY = "Recovery"


@dataclass(frozen=True)
class PhaseTypeDetails:
    """Human-readable details for a phase type."""

    label: str
    description: str


PHASE_TYPE_DETAILS: dict[PhaseType, PhaseTypeDetails] = {
    PhaseType.BASE: PhaseTypeDetails(
        label="Base",
        description=(
            "Establishes aerobic foundation and general fitness through "
            "high-volume, low-intensity work. Builds the endurance base "
            "required for harder training later."
        ),
    ),
    PhaseType.BUILD: PhaseTypeDetails(
        label="Build",
        description=(
            "Increases training stress with higher intensity and sport-specific "
            "workouts. Develops race-specific fitness while maintaining the aerobic base."
        ),
    ),
    PhaseType.PEAK: PhaseTypeDetails(
        label="Peak",
        description=(
            "Short, high-intensity phase immediately before a target race. "
            "Volume drops sharply while intensity peaks to bring the athlete to peak form."
        ),
    ),
    PhaseType.TAPER: PhaseTypeDetails(
        label="Taper",
        description=(
            "Reduces training load in the final days before competition to allow "
            "full recovery and super-compensation, maximising race-day performance."
        ),
    ),
    PhaseType.RECOVERY: PhaseTypeDetails(
        label="Recovery",
        description=(
            "Low-intensity, reduced-volume phase used after a race or hard block "
            "to allow physical and mental recuperation before the next training cycle begins."
        ),
    ),
}


def get_phase_type_details(phase_type: PhaseType) -> PhaseTypeDetails:
    """Return details for a phase type."""
    return PHASE_TYPE_DETAILS[phase_type]
