import type { TrainingOverviewData } from "@/types/dashboard";

interface TrainingOverviewProps {
  overview: TrainingOverviewData;
}

export function TrainingOverview({ overview }: TrainingOverviewProps) {
  return (
    <section>
      <h3 className="text-lg font-semibold text-zinc-950">Current training overview</h3>
      <div className="mt-3 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {overview.map((item) => (
          <article
            key={item.label}
            className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm"
          >
            <p className="text-sm font-medium text-zinc-500">{item.label}</p>
            <p className="mt-2 text-2xl font-semibold text-zinc-950">{item.value}</p>
            <p className="mt-2 text-sm leading-6 text-zinc-600">{item.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
