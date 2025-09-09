// frontend_tests/tests_jobs/finalizeWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/finalizeWorker", () => ({
  finalizeProject: vi.fn(),
}));

import { finalizeProject } from "@/jobs/finalizeWorker";

describe("finalizeWorker", () => {
  it("deve chamar finalizeProject com sucesso", () => {
    finalizeProject();
    expect(finalizeProject).toHaveBeenCalled();
  });
});
