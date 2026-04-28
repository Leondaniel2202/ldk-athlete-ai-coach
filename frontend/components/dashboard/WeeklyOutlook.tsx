import type { WeeklyWorkout } from "@/types/dashboard";

interface WeeklyOutlookProps {
  workouts: WeeklyWorkout[];
}

export function WeeklyOutlook({ workouts }: WeeklyOutlookProps) {
  return (
    <section className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-violet-700">Weekly outlook</p>
          <h3 className="mt-1 text-xl font-semibold text-zinc-950">Upcoming workouts</h3>
        </div>
        <p className="text-sm text-zinc-500">Mock data for the first app shell</p>
      </div>

      <div className="mt-5 grid gap-3">
        {workouts.map((workout) => (
          <article
            key={`${workout.day}-${workout.title}`}
            className="grid gap-3 rounded-lg border border-zinc-200 bg-stone-50 p-4 sm:grid-cols-[7rem_1fr_auto] sm:items-center"
          >
            <p className="text-sm font-semibold text-zinc-700">{workout.day}</p>
            <div>
              <h4 className="text-sm font-semibold text-zinc-950">{workout.title}</h4>
              <p className="mt-1 text-sm text-zinc-600">{workout.detail}</p>
            </div>
            <span className="w-fit rounded-lg bg-white px-3 py-1 text-xs font-semibold text-zinc-600 ring-1 ring-zinc-200">
              {workout.status}
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}
