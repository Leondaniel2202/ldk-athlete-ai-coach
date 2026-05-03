import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { PhaseCard } from "@/components/dashboard/PhaseCard";
import { PlanCard } from "@/components/dashboard/PlanCard";
import { TrainingOverview } from "@/components/dashboard/TrainingOverview";
import { WeeklyOutlook } from "@/components/dashboard/WeeklyOutlook";
import { getDashboardOverview } from "@/lib/api/dashboard/dashboard";

export default async function DashboardPage() {
  const data = await getDashboardOverview().catch(() => null);

  return (
    <div className="space-y-6">
      <DashboardHeader
        athleteName={data?.athlete_name ?? ""}
        summary={data?.summary ?? ""}
        nextAction={data?.next_action ?? ""}
      />

      <TrainingOverview overview={data?.overview ?? []} />

      <div className="grid gap-4 lg:grid-cols-2">
        {data?.current_plan && <PlanCard plan={data.current_plan} />}
        {data?.current_phase ? (
          <PhaseCard phase={data.current_phase} />
        ) : (
          <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
            <p className="text-sm font-semibold text-emerald-700">Current phase</p>
            <p className="mt-3 text-sm text-zinc-500">No active phase found.</p>
          </section>
        )}
      </div>

      <WeeklyOutlook workouts={data?.weekly_outlook ?? []} />
    </div>
  );
}
