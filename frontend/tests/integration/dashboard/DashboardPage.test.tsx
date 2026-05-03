import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import DashboardPage from "@/app/(app)/dashboard/page";
import { getDashboardOverview } from "@/lib/api/dashboard/dashboard";
import type { DashboardDataResponse } from "@/types/api/dashboard";

vi.mock("@/lib/api/dashboard/dashboard", () => ({
  getDashboardOverview: vi.fn(),
}));

const getDashboardOverviewMock = vi.mocked(getDashboardOverview);

const dashboardData: DashboardDataResponse = {
  athlete_name: "Lea",
  summary: "Training is on track for the next build block.",
  next_action: "Keep the next easy run conversational.",
  overview: [
    { label: "Weekly load", value: "7h", detail: "On target" },
    { label: "Adherence", value: "85%", detail: "One missed workout" },
  ],
  current_plan: {
    id: 1,
    name: "V2 build plan",
    plan_goal: "Build aerobic capacity",
    start_date_start: "2026-01-01T00:00:00Z",
    end_date_start: "2026-03-31T00:00:00Z",
  },
  current_phase: {
    id: 10,
    name: "Base phase",
    phase_type: "Base",
    timeframe_start: "2026-01-05T00:00:00Z",
    timeframe_end: "2026-02-02T00:00:00Z",
  },
  weekly_outlook: [
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
  ],
};

async function renderDashboard() {
  render(await DashboardPage());
}

describe("DashboardPage", () => {
  beforeEach(() => {
    getDashboardOverviewMock.mockReset();
  });

  it("renders mocked dashboard overview data", async () => {
    getDashboardOverviewMock.mockResolvedValue(dashboardData);

    await renderDashboard();

    expect(screen.getByRole("heading", { name: "Hello, Lea" })).toBeInTheDocument();
    expect(screen.getByText("Training is on track for the next build block.")).toBeInTheDocument();
    expect(screen.getByText("Keep the next easy run conversational.")).toBeInTheDocument();
  });

  it("shows the current plan, current phase, training overview, and weekly outlook", async () => {
    getDashboardOverviewMock.mockResolvedValue(dashboardData);

    await renderDashboard();

    expect(screen.getByRole("heading", { name: "V2 build plan" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Base phase" })).toBeInTheDocument();
    expect(screen.getByText("Weekly load")).toBeInTheDocument();
    expect(screen.getByText("7h")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Easy run" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Strength session" })).toBeInTheDocument();
    expect(screen.getByText("2 workouts")).toBeInTheDocument();
  });

  it("handles an empty weekly workout list", async () => {
    getDashboardOverviewMock.mockResolvedValue({
      ...dashboardData,
      weekly_outlook: [],
    });

    await renderDashboard();

    expect(screen.getByRole("heading", { name: "V2 build plan" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Base phase" })).toBeInTheDocument();
    expect(screen.getByText("0 workouts")).toBeInTheDocument();
  });

  it("renders the empty dashboard fallback when overview loading fails", async () => {
    getDashboardOverviewMock.mockRejectedValue(new Error("backend offline"));

    await renderDashboard();

    expect(screen.getByRole("heading", { name: "Hello," })).toBeInTheDocument();
    expect(screen.getByText("No active phase found.")).toBeInTheDocument();
    expect(screen.getByText("0 workouts")).toBeInTheDocument();
  });
});
