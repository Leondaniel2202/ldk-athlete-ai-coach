"use client";

import StatusBadge from "@/components/ui/StatusBadge";
import { useBackendStatus } from "@/hooks/useBackendStatus";

export default function Home() {
  const backendStatus = useBackendStatus();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 p-8 dark:bg-zinc-950">
      <div className="w-full max-w-lg rounded-2xl bg-white p-10 shadow-sm dark:bg-zinc-900">
        <h1 className="mb-2 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          LDK Athlete AI Coach
        </h1>
        <p className="mb-8 text-zinc-500 dark:text-zinc-400">Planning UI — frontend foundation</p>

        <div className="space-y-4">
          <div>
            <p className="mb-1 text-sm font-medium text-zinc-600 dark:text-zinc-400">
              Backend status
            </p>
            <StatusBadge status={backendStatus} />
          </div>

          <div className="rounded-lg border border-zinc-100 bg-zinc-50 px-4 py-3 dark:border-zinc-800 dark:bg-zinc-800/50">
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              This is the initial frontend scaffold for the V2 planning UI. Feature screens will be
              added in upcoming iterations.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
