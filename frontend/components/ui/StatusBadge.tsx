import type { BackendStatus } from "@/hooks/useBackendStatus";

interface StatusBadgeProps {
  status: BackendStatus;
}

const labels: Record<BackendStatus, string> = {
  loading: "Checking backend…",
  connected: "Backend connected",
  error: "Backend unreachable",
};

const colours: Record<BackendStatus, string> = {
  loading: "bg-zinc-100 text-zinc-500",
  connected: "bg-green-100 text-green-700",
  error: "bg-red-100 text-red-700",
};

/**
 * Displays the current backend connectivity status as a small badge.
 */
export default function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${colours[status]}`}
    >
      {labels[status]}
    </span>
  );
}
