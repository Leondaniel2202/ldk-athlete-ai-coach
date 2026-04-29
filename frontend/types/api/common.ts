export type ApiDateString = string;
export type ApiDateTimeString = string;

export interface ApiErrorDetail {
  detail: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

export type PlanStatus = "Active" | "Past" | "Future" | "Unknown";

export type PhaseStatus = "Active" | "Past" | "Future" | "Unknown";

export type WorkoutStatus = "Open" | "Done" | "Missed" | "Skipped" | "Cancelled" | "Unknown";

export interface ContextMetadataResponse {
  as_of_date: ApiDateString;
  timezone: string;
}

export interface PhaseWeekContextMetadataResponse extends ContextMetadataResponse {
  phase_week_number: number;
  phase_week_start_date: ApiDateTimeString;
  phase_week_end_date: ApiDateTimeString;
}
