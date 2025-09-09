// frontend_tests/tests_jobs/filterWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/filterWorker", () => ({
  applyFilter: vi.fn(),
}));

import { applyFilter } from "@/jobs/filterWorker";

describe("filterWorker", () => {
  it("deve chamar applyFilter com tipo de filtro", () => {
    applyFilter("sepia");
    expect(applyFilter).toHaveBeenCalledWith("sepia");
  });
});
