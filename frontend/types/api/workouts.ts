import type { ApiDateTimeString, WorkoutStatus } from "./common";

export interface WorkoutSummaryResponse {
  id: number;
  name: string;
  category: string | null;
  date_start: ApiDateTimeString | null;
  done_date_start: ApiDateTimeString | null;
  status : WorkoutStatus;
  
}
