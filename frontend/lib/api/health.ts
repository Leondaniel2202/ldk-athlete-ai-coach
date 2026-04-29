/**
 * Backend health check endpoint.
 */

import type { HealthStatus, RootStatus } from "@/types/api/system";
import { apiClient } from "./client";

export async function getHealth(): Promise<HealthStatus> {
  return apiClient.get<HealthStatus>("/api/v1/system/health");
}

export async function getRoot(): Promise<RootStatus> {
  return apiClient.get<RootStatus>("/");
}
