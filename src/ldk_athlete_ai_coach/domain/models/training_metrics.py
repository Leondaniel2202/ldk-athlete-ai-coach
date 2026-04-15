from dataclasses import dataclass


@dataclass
class MetricAdherence:
    """Response schema for adherence to a specific training metric."""

    metric_name: str
    adherence_percentage: float


@dataclass
class TrainingMetrics:
    """Response schema for training metrics of a given timeframe."""

    planned_training_load: float
    actual_training_load: float
    metric_adherence: list[MetricAdherence]
