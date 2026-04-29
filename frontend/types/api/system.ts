export interface HealthCheckResponse {
  status: string;
}

export interface RootStatusResponse {
  message: string;
}

export type HealthStatus = HealthCheckResponse;
export type RootStatus = RootStatusResponse;
