import type { AnalyzePhaseContextResponse } from "@/types/api/ai";
import { apiClient } from "../client";

export async function getDashboardOverview(phaseId: string): Promise<AnalyzePhaseContextResponse> {
    return apiClient.get<AnalyzePhaseContextResponse>(`/api/v1/ai/analysis/phase-context/${phaseId}`);
}
