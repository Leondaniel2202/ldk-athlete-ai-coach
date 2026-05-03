import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WeeklyOutlook } from "@/components/dashboard/WeeklyOutlook";
import type { WorkoutSummaryResponse } from "@/types/api/workouts";

const workouts: WorkoutSummaryResponse[] = [
  {
    id: 100,
    name: "Easy run",
    category: "Run",
    date_start: "2026-01-05T08:00:00Z",
    done_date_start: null,
    status: "Open",
  },
  {
    id: 101,
    name: "Strength session",
    category: "Strength",
    date_start: "2026-01-07T17:00:00Z",
    done_date_start: null,
    status: "Open",
  },
];

describe("WeeklyOutlook", () => {
  it("renders upcoming workouts", () => {
    render(<WeeklyOutlook workouts={workouts} />);

    expect(screen.getByRole("heading", { name: "Upcoming workouts" })).toBeInTheDocument();
    expect(screen.getByText("2 workouts")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Easy run" })).toBeInTheDocument();
    expect(screen.getByText("Run")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Strength session" })).toBeInTheDocument();
    expect(screen.getByText("Strength")).toBeInTheDocument();
    expect(screen.getAllByText("Open")).toHaveLength(2);
  });

  it("renders an empty weekly workout count", () => {
    render(<WeeklyOutlook workouts={[]} />);

    expect(screen.getByRole("heading", { name: "Upcoming workouts" })).toBeInTheDocument();
    expect(screen.getByText("0 workouts")).toBeInTheDocument();
  });
});
