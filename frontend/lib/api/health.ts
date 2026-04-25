/**
 * Backend health check endpoint.
 */

import { apiClient } from "./client";

export interface HealthStatus {
  status: string;
}

export interface RootStatus {
  message: string;
}

export async function getHealth(): Promise<HealthStatus> {
  return apiClient.get<HealthStatus>("/api/v1/system/health");
}

export async function getRoot(): Promise<RootStatus> {
  return apiClient.get<RootStatus>("/");
}
