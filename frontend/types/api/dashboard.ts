import { PhaseSummaryResponse } from "./phases";
import { PlanSummaryResponse } from "./plans";
import { WorkoutSummaryResponse } from "./workouts";

export interface OverviewItem {
  label: string;
  value: string | null;
  detail: string | null;
}

export type TrainingOverviewData = OverviewItem[];

export interface DashboardData {
  athleteName: string;
  summary: string;
  nextAction: string;
  overview: TrainingOverviewData;
  currentPlan: PlanSummaryResponse | null;
  currentPhase: PhaseSummaryResponse | null;
  weeklyOutlook: WorkoutSummaryResponse[];
}
