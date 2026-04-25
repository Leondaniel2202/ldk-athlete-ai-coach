from dataclasses import dataclass

from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus


@dataclass
class MetricAdherence:
    """Response schema for adherence to a specific training metric."""

    metric_name: str
    adherence_percentage: float | None


@dataclass
class TrainingMetrics:
    """Response schema for training metrics of a given timeframe."""

    planned_training_load: float
    actual_training_load: float
    metric_adherence: list[MetricAdherence]
    included_statuses: set[WorkoutStatus]
