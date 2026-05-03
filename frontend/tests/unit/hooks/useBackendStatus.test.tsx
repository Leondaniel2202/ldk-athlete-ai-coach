import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useBackendStatus } from "@/hooks/useBackendStatus";
import { getHealth } from "@/lib/api/health";

vi.mock("@/lib/api/health", () => ({
  getHealth: vi.fn(),
}));

const getHealthMock = vi.mocked(getHealth);

describe("useBackendStatus", () => {
  beforeEach(() => {
    getHealthMock.mockReset();
  });

  it("starts in loading and becomes connected after a successful health check", async () => {
    getHealthMock.mockResolvedValue({ status: "ok" });

    const { result } = renderHook(() => useBackendStatus());

    expect(result.current).toBe("loading");

    await waitFor(() => {
      expect(result.current).toBe("connected");
    });
  });

  it("starts in loading and becomes error after a failed health check", async () => {
    getHealthMock.mockRejectedValue(new Error("backend offline"));

    const { result } = renderHook(() => useBackendStatus());

    expect(result.current).toBe("loading");

    await waitFor(() => {
      expect(result.current).toBe("error");
    });
  });
});
