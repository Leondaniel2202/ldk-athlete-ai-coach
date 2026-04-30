import type { PhaseSummaryResponse } from "@/types/api/phases";

interface PhaseCardProps {
  phase: PhaseSummaryResponse;
}

function formatTimeframe(start: string | null, end: string | null): string {
  if (!start || !end) return "—";
  const fmt = (d: string) =>
    new Date(d).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
  return `${fmt(start)} – ${fmt(end)}`;
}

export function PhaseCard({ phase }: PhaseCardProps) {
  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-semibold text-emerald-700">Current phase</p>
      <h3 className="mt-2 text-xl font-semibold text-zinc-950">{phase.name}</h3>

      <dl className="mt-5 grid gap-3 sm:grid-cols-2">
        <div>
          <dt className="text-xs font-medium text-zinc-500">Phase type</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">{phase.phase_type ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-zinc-500">Timeframe</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">
            {formatTimeframe(phase.timeframe_start, phase.timeframe_end)}
          </dd>
        </div>
      </dl>
    </section>
  );
}
