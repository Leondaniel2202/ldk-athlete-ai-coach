import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import AppShell from "@/components/app-shell/AppShell";

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
}));

vi.mock("@/hooks/useBackendStatus", () => ({
  useBackendStatus: () => "connected",
}));

describe("AppShell", () => {
  it("renders the shell and supports keyboard navigation", async () => {
    const user = userEvent.setup();

    render(
      <AppShell>
        <p>Dashboard content</p>
      </AppShell>,
    );

    expect(screen.getByRole("heading", { name: "Athlete AI Coach" })).toBeInTheDocument();
    expect(screen.getByText("Dashboard content")).toBeInTheDocument();
    expect(screen.getByText("Backend connected")).toBeInTheDocument();

    const dashboardLink = screen.getByRole("link", { name: "Dashboard" });
    expect(dashboardLink).toHaveAttribute("aria-current", "page");

    const plannerLink = screen.getByRole("link", { name: "Planner" });
    await user.tab();
    await user.tab();

    expect(plannerLink).toHaveFocus();
    expect(plannerLink).toHaveAttribute("href", "/planner");
  });
});
