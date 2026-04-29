import type { ApiDateTimeString } from "./common";

export interface PlanSummaryResponse {
  id: number;
  name: string;
  plan_goal: string | null;
  start_date_start: ApiDateTimeString | null;
  end_date_start: ApiDateTimeString | null;
}