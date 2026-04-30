import type { DashboardDataResponse } from "@/types/api/dashboard";
import { apiClient } from "../client";

export async function getDashboardOverview(): Promise<DashboardDataResponse> {
  return apiClient.get<DashboardDataResponse>("/api/v1/dashboard/overview");
}
