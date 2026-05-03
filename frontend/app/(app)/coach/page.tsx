import { PlaceholderPage } from "@/components/app-shell/PlaceholderPage";

const coachItems = [
  "AI coaching feedback",
  "Recommendations",
  "Generated workouts, phases, and plans",
  "Structured coaching conversations",
];

export default function CoachPage() {
  return (
    <PlaceholderPage
      eyebrow="Coach"
      title="Turn training context into coaching support"
      description="This area will host AI-assisted feedback, recommendation flows, and structured coaching conversations."
      items={coachItems}
    />
  );
}
