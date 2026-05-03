import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StatusBadge from "@/components/ui/StatusBadge";
import type { BackendStatus } from "@/hooks/useBackendStatus";

describe("StatusBadge", () => {
  it.each<[BackendStatus, string]>([
    ["loading", "Checking backend..."],
    ["connected", "Backend connected"],
    ["error", "Backend unreachable"],
  ])("renders the %s label", (status, label) => {
    render(<StatusBadge status={status} />);

    expect(screen.getByText(label)).toBeInTheDocument();
  });
});
