import type { CurrentPlan } from "@/types/api/dashboard";

interface PlanCardProps {
  plan: CurrentPlan;
}

export function PlanCard({ plan }: PlanCardProps) {
  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-semibold text-blue-700">Current plan</p>
      <h3 className="mt-2 text-xl font-semibold text-zinc-950">{plan.name}</h3>
      <p className="mt-3 text-sm leading-6 text-zinc-600">{plan.description}</p>

      <dl className="mt-5 grid gap-3 sm:grid-cols-2">
        <div>
          <dt className="text-xs font-medium text-zinc-500">Focus</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">{plan.focus}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-zinc-500">Timeline</dt>
          <dd className="mt-1 text-sm font-semibold text-zinc-900">{plan.timeline}</dd>
        </div>
      </dl>
    </section>
  );
}
