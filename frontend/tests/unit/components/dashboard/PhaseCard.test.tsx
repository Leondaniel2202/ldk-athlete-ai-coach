import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PhaseCard } from "@/components/dashboard/PhaseCard";
import type { PhaseSummaryResponse } from "@/types/api/phases";

const phase: PhaseSummaryResponse = {
  id: 10,
  name: "Base phase",
  phase_type: "Base",
  timeframe_start: "2026-01-05T00:00:00Z",
  timeframe_end: "2026-02-02T00:00:00Z",
};

describe("PhaseCard", () => {
  it("renders the current phase summary", () => {
    render(<PhaseCard phase={phase} />);

    expect(screen.getByText("Current phase")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Base phase" })).toBeInTheDocument();
    expect(screen.getByText("Base")).toBeInTheDocument();
    expect(screen.getByText(/Jan 5, 2026/)).toBeInTheDocument();
    expect(screen.getByText(/Feb 2, 2026/)).toBeInTheDocument();
  });
});
