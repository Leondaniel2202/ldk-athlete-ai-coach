import type { PhaseWeekContextResponse } from "@/types/api/phase-context";

interface PhaseCardProps {
  phase: PhaseWeekContextResponse;
}

function getWeekLabel(phase: PhaseWeekContextResponse): string {
  const { phase_week_number: weekNumber, phase_week_start_date: weekStart, phase_week_end_date: weekEnd } = phase.metadata;
  const timeframeStart = phase.phase_summary.timeframe_start;
  const timeframeEnd = phase.phase_summary.timeframe_end;

  if (!timeframeStart || !timeframeEnd) {
    return `Week ${weekNumber}`;
  }

  const totalWeeks = Math.max(
    1,
    Math.ceil((new Date(timeframeEnd).getTime() - new Date(timeframeStart).getTime()) / (7 * 24 * 60 * 60 * 1000)),
  );

  return `Week ${weekNumber} of ${totalWeeks} (${new Date(weekStart).toLocaleDateString()} - ${new Date(weekEnd).toLocaleDateString()})`;
}

export function PhaseCard({ phase }: PhaseCardProps) {
  const focus = phase.phase_summary.phase_type ?? phase.plan_summary.plan_goal ?? "—";
  const weekLabel = getWeekLabel(phase);

  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-semibold text-emerald-700">Current phase</p>
      <h3 className="mt-2 text-xl font-semibold text-zinc-950">{phase.phase_summary.name}</h3>
      <p className="mt-3 text-sm leading-6 text-zinc-600">{phase.plan_summary.name}</p>

      <dl className="mt-5 grid gap-3 sm:grid-cols-2">
        <div>
          <dt className="text-xs font-medium text-zinc-500">Phase focus</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">{focus}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-zinc-500">Current week</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">{weekLabel}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-zinc-500">Status</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">{phase.phase_status}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-zinc-500">Planned workouts</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">{phase.adherence.planned_workouts}</dd>
        </div>
      </dl>
    </section>
  );
}
