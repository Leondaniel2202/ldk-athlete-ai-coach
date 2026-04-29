import type { Phase } from "@/types/api";
import { apiClient } from "../client";

export async function getCurrentPhaseWeekContext(): Promise<Phase> {
  return apiClient.get<Phase>("/api/v1/context/phase/week/current");
}
