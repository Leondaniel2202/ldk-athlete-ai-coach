import type { ApiDateTimeString } from "./common";

export interface PhaseSummaryResponse {
  id: number;
  name: string;
  phase_type: string | null;
  timeframe_start: ApiDateTimeString | null;
  timeframe_end: ApiDateTimeString | null;
}
