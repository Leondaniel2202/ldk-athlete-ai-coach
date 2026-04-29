import type { ApiDateTimeString } from "./common";
import type { SessionResponse } from "./sessions";

export interface WorkoutResponse {
  id: number;
  notion_page_id: string;
  notion_url: string;
  name: string;
  date_start: ApiDateTimeString | null;
  date_end: ApiDateTimeString | null;
  date_is_datetime: boolean;
  category: string | null;
  difficulty: string | null;
  equipment: string[];
  impact: string | null;
  metrics_to_record: string[];
  purpose: string[];
  primarily_used_muscle_group: string[];
  planned_distance_km: number | null;
  planned_duration_min: number | null;
  planned_rpe: number | null;
  planned_training_load: number | null;
  planned_week_number: number | null;
  actual_duration_min: number | null;
  actual_distance_km: number | null;
  actual_training_load: number | null;
  actual_calories_burned_kcal: number | null;
  weighted_hrr_intensity_sum: number | null;
  actual_hrr_intensity: number | null;
  actual_rpe: number | null;
  done_date_start: ApiDateTimeString | null;
  done_date_end: ApiDateTimeString | null;
  done_date_is_datetime: boolean;
  status: string | null;
  training_load_method: string | null;
  additional_info: string | null;
  cancelled: boolean;
  skipped: boolean;
  phase_id: number | null;
}

export interface WorkoutContentResponse extends WorkoutResponse {
  notion_page_content: string | null;
}

export interface WorkoutDetailResponse extends WorkoutContentResponse {
  tracked_sessions: SessionResponse[];
}

export interface WorkoutSummaryResponse {
  id: number;
  name: string;
  date_start: ApiDateTimeString | null;
  date_end: ApiDateTimeString | null;
}
