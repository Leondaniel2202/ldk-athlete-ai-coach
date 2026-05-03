import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlanCard } from "@/components/dashboard/PlanCard";
import type { PlanSummaryResponse } from "@/types/api/plans";

const plan: PlanSummaryResponse = {
  id: 1,
  name: "V2 build plan",
  plan_goal: "Build aerobic capacity",
  start_date_start: "2026-01-01T00:00:00Z",
  end_date_start: "2026-03-31T00:00:00Z",
};

describe("PlanCard", () => {
  it("renders the current plan summary", () => {
    render(<PlanCard plan={plan} />);

    expect(screen.getByText("Current plan")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "V2 build plan" })).toBeInTheDocument();
    expect(screen.getAllByText("Build aerobic capacity")).toHaveLength(2);
    expect(screen.getByText(/Jan 2026/)).toBeInTheDocument();
    expect(screen.getByText(/Mar 2026/)).toBeInTheDocument();
  });
});
