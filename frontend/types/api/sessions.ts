import type { ApiDateTimeString } from "./common";

export interface SessionResponse {
  id: number;
  notion_page_id: string;
  notion_url: string;
  name: string;
  source: string | null;
  session_type: string | null;
  external_id: string | null;
  start_start: ApiDateTimeString | null;
  start_end: ApiDateTimeString | null;
  start_is_datetime: boolean;
  end_start: ApiDateTimeString | null;
  end_end: ApiDateTimeString | null;
  end_is_datetime: boolean;
  active_energy_kj: number | null;
  active_energy_burned_kj: number | null;
  avg_hr: number | null;
  max_hr: number | null;
  calories_kcal: number | null;
  distance_km: number | null;
  duration_min: number | null;
  elevation_ascended_m: number | null;
  elevation_descended_m: number | null;
  intensity_kcal_per_hr_kg: number | null;
  step_cadence_count_per_min: number | null;
  steps: number | null;
  workout_id: number | null;
}

export interface SessionSummaryResponse {
  id: number;
  name: string;
  source: string | null;
  session_type: string | null;
  start_start: ApiDateTimeString | null;
  end_end: ApiDateTimeString | null;
}
