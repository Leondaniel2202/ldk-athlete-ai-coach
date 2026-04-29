import type { ApiDateTimeString } from "./common";
import type { PhaseDetailResponse } from "./phases";

export interface PlanResponse {
  id: number;
  notion_page_id: string;
  notion_url: string;
  name: string;
  plan_goal: string | null;
  constraints: string | null;
  rules_weekly_rhythm: string | null;
  start_date_start: ApiDateTimeString | null;
  start_date_end: ApiDateTimeString | null;
  start_date_is_datetime: boolean;
  end_date_start: ApiDateTimeString | null;
  end_date_end: ApiDateTimeString | null;
  end_date_is_datetime: boolean;
}

export interface PlanDetailResponse extends PlanResponse {
  phases: PhaseDetailResponse[];
}

export interface PlanSummaryResponse {
  id: number;
  name: string;
  plan_goal: string | null;
  start_date_start: ApiDateTimeString | null;
  end_date_end: ApiDateTimeString | null;
}
