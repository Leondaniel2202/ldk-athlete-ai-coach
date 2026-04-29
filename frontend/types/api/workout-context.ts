import type { ContextMetadataResponse, WorkoutStatus } from "./common";
import type { PhaseSummaryResponse } from "./phases";
import type { PlanSummaryResponse } from "./plans";
import type { WorkoutDetailResponse } from "./workouts";

export interface WorkoutContextResponse {
  metadata: ContextMetadataResponse;
  plan_summary: PlanSummaryResponse | null;
  phase_summary: PhaseSummaryResponse | null;
  workout_status: WorkoutStatus;
  workout_details: WorkoutDetailResponse;
}
