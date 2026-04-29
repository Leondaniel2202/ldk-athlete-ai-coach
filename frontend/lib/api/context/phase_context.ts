import type { PhaseWeekContextResponse } from "@/types/api/phase-context";
import { apiClient } from "../client";

export async function getCurrentPhaseWeekContext(): Promise<PhaseWeekContextResponse> {
  return apiClient.get<PhaseWeekContextResponse>("/api/v1/context/phase/week/current");
}
