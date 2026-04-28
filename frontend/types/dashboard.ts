export interface OverviewItem {
  label: string;
  value: string;
  detail: string;
}

export type TrainingOverviewData = OverviewItem[];

export interface CurrentPlan {
  name: string;
  description: string;
  focus: string;
  timeline: string;
}

export interface CurrentPhase {
  name: string;
  description: string;
  focus: string;
  weekLabel: string;
}

export interface WeeklyWorkout {
  day: string;
  title: string;
  detail: string;
  status: string;
}

export interface DashboardData {
  athleteName: string;
  summary: string;
  nextAction: string;
  overview: TrainingOverviewData;
  currentPlan: CurrentPlan;
  currentPhase: CurrentPhase;
  weeklyOutlook: WeeklyWorkout[];
}
