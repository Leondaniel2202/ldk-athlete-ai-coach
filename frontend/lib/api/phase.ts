import type { Phase } from "@/types/api";
import { apiClient } from "./client";

export async function getCurrentPhase(): Promise<Phase> {
  return apiClient.get<Phase>("/api/v1/resources/phases/current");
}
