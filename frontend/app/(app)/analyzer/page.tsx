import { PlaceholderPage } from "@/components/app-shell/PlaceholderPage";

const analyzerItems = [
  "Training metrics",
  "Adherence",
  "Weekly and phase-level analysis",
  "Trends and insights",
];

export default function AnalyzerPage() {
  return (
    <PlaceholderPage
      eyebrow="Analyzer"
      title="Review performance and training signals"
      description="This area will surface backend-owned analysis views for training load, execution, and longer-term patterns."
      items={analyzerItems}
    />
  );
}
