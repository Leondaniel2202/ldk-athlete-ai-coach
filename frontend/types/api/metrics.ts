import type { ApiDateString, WorkoutStatus } from "./common";

export interface MetricAdherence {
  metric_name: string;
  adherence_percentage: number | null;
}

export interface TrainingMetrics {
  planned_training_load: number;
  actual_training_load: number;
  metric_adherence: MetricAdherence[];
  included_statuses: WorkoutStatus[];
}

export interface MetricAdherenceResponse {
  metric_name: string;
  adherence_percentage: number | null;
}

export interface TrainingMetricsResponse {
  timeframe_start: ApiDateString | null;
  timeframe_end: ApiDateString | null;
  training_metrics: TrainingMetrics;
}
