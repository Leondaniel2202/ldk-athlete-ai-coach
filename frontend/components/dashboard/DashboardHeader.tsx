interface DashboardHeaderProps {
  athleteName: string;
  summary: string;
  nextAction: string;
}

export function DashboardHeader({ athleteName, summary, nextAction }: DashboardHeaderProps) {
  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm sm:p-6">
      <p className="text-sm font-semibold text-emerald-700">Dashboard</p>
      <h2 className="mt-2 text-3xl font-semibold tracking-tight text-zinc-950">
        Hello, {athleteName}
      </h2>
      <p className="mt-3 max-w-3xl text-base leading-7 text-zinc-600">{summary}</p>
      <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
        <p className="text-sm font-medium text-amber-900">{nextAction}</p>
      </div>
    </section>
  );
}
