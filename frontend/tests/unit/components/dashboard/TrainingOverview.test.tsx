import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrainingOverview } from "@/components/dashboard/TrainingOverview";
import type { TrainingOverviewData } from "@/types/api/dashboard";

const overview: TrainingOverviewData = [
  { label: "Weekly load", value: "7h", detail: "On target" },
  { label: "Adherence", value: "85%", detail: "One missed workout" },
];

describe("TrainingOverview", () => {
  it("renders overview items", () => {
    render(<TrainingOverview overview={overview} />);

    expect(screen.getByRole("heading", { name: "Current training overview" })).toBeInTheDocument();
    expect(screen.getByText("Weekly load")).toBeInTheDocument();
    expect(screen.getByText("7h")).toBeInTheDocument();
    expect(screen.getByText("On target")).toBeInTheDocument();
    expect(screen.getByText("Adherence")).toBeInTheDocument();
    expect(screen.getByText("85%")).toBeInTheDocument();
    expect(screen.getByText("One missed workout")).toBeInTheDocument();
  });
});
