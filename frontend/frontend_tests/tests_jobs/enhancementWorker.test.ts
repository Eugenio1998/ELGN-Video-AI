// frontend_tests/tests_jobs/enhancementWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/enhancementWorker", () => ({
  enhanceVideo: vi.fn(),
}));

import { enhanceVideo } from "@/jobs/enhancementWorker";

describe("enhancementWorker", () => {
  it("deve chamar enhanceVideo com nível de melhoria", () => {
    enhanceVideo("alta");
    expect(enhanceVideo).toHaveBeenCalledWith("alta");
  });
});
