import type { WorkoutAdherenceSummaryResponse } from "./adherence";
import type {
  ContextMetadataResponse,
  PhaseStatus,
  PhaseWeekContextMetadataResponse,
} from "./common";
import type { TrainingMetricsResponse } from "./metrics";
import type { PhaseResponse, PhaseSummaryResponse } from "./phases";
import type { PlanSummaryResponse } from "./plans";
import type { WorkoutContentResponse, WorkoutDetailResponse } from "./workouts";

export interface PhaseContextResponse {
  metadata: ContextMetadataResponse;
  plan_summary: PlanSummaryResponse;
  phase_status: PhaseStatus;
  phase: PhaseResponse;
  open_workouts: WorkoutContentResponse[];
  done_workouts: WorkoutDetailResponse[];
  weekly_metrics: TrainingMetricsResponse[];
  adherence: WorkoutAdherenceSummaryResponse;
  data_gaps: string[];
}

export interface PhaseWeekContextResponse {
  metadata: PhaseWeekContextMetadataResponse;
  plan_summary: PlanSummaryResponse;
  phase_status: PhaseStatus;
  phase_summary: PhaseSummaryResponse;
  workouts: WorkoutDetailResponse[];
  metrics: TrainingMetricsResponse;
  adherence: WorkoutAdherenceSummaryResponse;
  data_gaps: string[];
}
