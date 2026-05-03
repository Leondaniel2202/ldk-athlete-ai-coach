export interface WorkoutAdherenceSummaryResponse {
  planned_workouts: number;
  completed_workouts: number;
  skipped_workouts: number;
  unknown_workouts: number;
  completion_ratio: number | null;
}
