import { PlaceholderPage } from "@/components/app-shell/PlaceholderPage";

const plannerItems = ["Plan management", "Phase management", "Week-based workout planning"];

export default function PlannerPage() {
  return (
    <PlaceholderPage
      eyebrow="Planner"
      title="Structure upcoming training blocks"
      description="This area will become the workspace for organizing plans, phases, and weekly workout structure."
      items={plannerItems}
    />
  );
}
