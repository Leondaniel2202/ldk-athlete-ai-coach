from datetime import date

from pydantic import BaseModel, ConfigDict


class MetricAdherenceResponse(BaseModel):
    """Response schema for adherence to a specific training metric."""

    model_config = ConfigDict(from_attributes=True)

    metric_name: str
    adherence_percentage: float | None


class TrainingMetricsResponse(BaseModel):
    """Response schema for training metrics of a given timeframe."""

    model_config = ConfigDict(from_attributes=True)

    timeframe_start: date | None
    timeframe_end: date | None
    planned_training_load: float
    actual_training_load: float
    metric_adherence: MetricAdherenceResponse


class WeeklyMetricsResponse(BaseModel):
    """Response schema for a week's worth of training metrics."""

    model_config = ConfigDict(from_attributes=True)

    week_number: int
    metrics: TrainingMetricsResponse
