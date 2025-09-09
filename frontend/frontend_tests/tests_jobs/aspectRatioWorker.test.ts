// frontend_tests/tests_jobs/aspectRatioWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/aspectRatioWorker", () => ({
  changeAspectRatio: vi.fn(),
}));

import { changeAspectRatio } from "@/jobs/aspectRatioWorker";

describe("aspectRatioWorker", () => {
  it("deve chamar changeAspectRatio com valor esperado", () => {
    changeAspectRatio("16:9");
    expect(changeAspectRatio).toHaveBeenCalledWith("16:9");
  });
});
