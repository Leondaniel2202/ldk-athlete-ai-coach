import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { PhaseCard } from "@/components/dashboard/PhaseCard";
import { PlanCard } from "@/components/dashboard/PlanCard";
import { TrainingOverview } from "@/components/dashboard/TrainingOverview";
import { WeeklyOutlook } from "@/components/dashboard/WeeklyOutlook";
import { dashboardData } from "@/lib/mock-data/dashboard";
import { getCurrentPhase } from "@/lib/api/phase";

export default async function DashboardPage() {
  const phase = await getCurrentPhase().catch(() => null);

  return (
    <div className="space-y-6">
      <DashboardHeader
        athleteName={dashboardData.athleteName}
        summary={dashboardData.summary}
        nextAction={dashboardData.nextAction}
      />

      <TrainingOverview overview={dashboardData.overview} />

      <div className="grid gap-4 lg:grid-cols-2">
        <PlanCard plan={dashboardData.currentPlan} />
        {phase ? (
          <PhaseCard phase={phase} />
        ) : (
          <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
            <p className="text-sm font-semibold text-emerald-700">Current phase</p>
            <p className="mt-3 text-sm text-zinc-500">No active phase found.</p>
          </section>
        )}
      </div>

      <WeeklyOutlook workouts={dashboardData.weeklyOutlook} />
    </div>
  );
}
