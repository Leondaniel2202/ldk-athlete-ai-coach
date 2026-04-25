from datetime import date

from pydantic import BaseModel, ConfigDict

from ldk_athlete_ai_coach.domain.models.training_metrics import TrainingMetrics


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
    training_metrics: TrainingMetrics
