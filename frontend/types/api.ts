/**
 * Common shared types used across the frontend.
 */

/** Generic API error shape returned by the backend. */
export interface ApiErrorDetail {
  detail: string;
}

/** Generic paginated response wrapper. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

/** Phase resource returned by GET /api/v1/resources/phases/current */
export interface Phase {
  id: number;
  notion_page_id: string;
  notion_url: string;
  name: string;
  notes: string | null;
  phase_type: string | null;
  focus_tags: string[];
  weekly_structure: string | null;
  timeframe_start: string | null;
  timeframe_end: string | null;
  timeframe_is_datetime: boolean;
  plan_id: number | null;
  nutrition_guideline_id: number | null;
}
