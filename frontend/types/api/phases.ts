import type { ApiDateTimeString } from "./common";
import type { WorkoutDetailResponse } from "./workouts";

export interface PhaseResponse {
  id: number;
  notion_page_id: string;
  notion_url: string;
  name: string;
  notes: string | null;
  phase_type: string | null;
  focus_tags: string[];
  weekly_structure: string | null;
  timeframe_start: ApiDateTimeString | null;
  timeframe_end: ApiDateTimeString | null;
  timeframe_is_datetime: boolean;
  plan_id: number | null;
  nutrition_guideline_id: number | null;
}

export interface PhaseDetailResponse extends PhaseResponse {
  workouts: WorkoutDetailResponse[];
}

export interface PhaseSummaryResponse {
  id: number;
  name: string;
  phase_type: string | null;
  timeframe_start: ApiDateTimeString | null;
  timeframe_end: ApiDateTimeString | null;
}

export type Phase = PhaseResponse;
