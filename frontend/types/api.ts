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
