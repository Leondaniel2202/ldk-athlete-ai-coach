export interface AnalyzePhaseContextRequest {
  instruction?: string | null;
}

export interface AnalyzePhaseContextResponse {
  summary: string;
  phase_focus: string;
  positives: string[];
  concerns: string[];
  recommendation: string;
}

export interface AnalyzeWorkoutContextRequest {
  instruction?: string | null;
}

export interface AnalyzeWorkoutContextResponse {
  summary: string;
  workout_focus: string;
  positives: string[];
  concerns: string[];
  recommendation: string;
}
