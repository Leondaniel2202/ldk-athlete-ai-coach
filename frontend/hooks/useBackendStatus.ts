"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api/health";

export type BackendStatus = "loading" | "connected" | "error";

/**
 * Hook that checks whether the backend API is reachable.
 * Returns the current connectivity status.
 */
export function useBackendStatus(): BackendStatus {
  const [status, setStatus] = useState<BackendStatus>("loading");

  useEffect(() => {
    let cancelled = false;

    getHealth()
      .then(() => {
        if (!cancelled) setStatus("connected");
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return status;
}
