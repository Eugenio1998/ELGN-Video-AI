// frontend_tests/tests_jobs/resolutionWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/resolutionWorker", () => ({
  changeResolution: vi.fn(),
}));

import { changeResolution } from "@/jobs/resolutionWorker";

describe("resolutionWorker", () => {
  it("deve chamar changeResolution com resolução correta", () => {
    changeResolution("1080p");
    expect(changeResolution).toHaveBeenCalledWith("1080p");
  });
});
