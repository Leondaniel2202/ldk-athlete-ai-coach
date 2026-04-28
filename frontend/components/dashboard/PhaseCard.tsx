import type { Phase } from "@/types/api";

interface PhaseCardProps {
  phase: Phase;
}

function getWeekLabel(start: string | null, end: string | null): string {
  if (!start) return "—";
  const startDate = new Date(start);
  const now = new Date();
  const weekNum = Math.max(1, Math.ceil((now.getTime() - startDate.getTime()) / (7 * 24 * 60 * 60 * 1000)));
  if (end) {
    const totalWeeks = Math.ceil((new Date(end).getTime() - startDate.getTime()) / (7 * 24 * 60 * 60 * 1000));
    return `Week ${weekNum} of ${totalWeeks}`;
  }
  return `Week ${weekNum}`;
}

export function PhaseCard({ phase }: PhaseCardProps) {
  const focus = phase.phase_type ?? (phase.focus_tags.length > 0 ? phase.focus_tags.join(", ") : "—");
  const weekLabel = getWeekLabel(phase.timeframe_start, phase.timeframe_end);

  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-semibold text-emerald-700">Current phase</p>
      <h3 className="mt-2 text-xl font-semibold text-zinc-950">{phase.name}</h3>
      {phase.notes && (
        <p className="mt-3 text-sm leading-6 text-zinc-600">{phase.notes}</p>
      )}

      <dl className="mt-5 grid gap-3 sm:grid-cols-2">
        <div>
          <dt className="text-xs font-medium text-zinc-500">Phase focus</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">{focus}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-zinc-500">Current week</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">{weekLabel}</dd>
        </div>
      </dl>
    </section>
  );
}
