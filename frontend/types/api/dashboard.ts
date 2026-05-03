import { PhaseSummaryResponse } from "./phases";
import { PlanSummaryResponse } from "./plans";
import { WorkoutSummaryResponse } from "./workouts";

export interface OverviewItemResponse {
  label: string;
  value: string | null;
  detail: string | null;
}

export type TrainingOverviewData = OverviewItemResponse[];

export interface DashboardDataResponse {
  athlete_name: string;
  summary: string;
  next_action: string;
  overview: TrainingOverviewData;
  current_plan: PlanSummaryResponse | null;
  current_phase: PhaseSummaryResponse | null;
  weekly_outlook: WorkoutSummaryResponse[];
}
