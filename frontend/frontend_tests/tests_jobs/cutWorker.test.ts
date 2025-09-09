// frontend_tests/tests_jobs/cutWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/cutWorker", () => ({
  autoCut: vi.fn(),
}));

import { autoCut } from "@/jobs/cutWorker";

describe("cutWorker", () => {
  it("deve chamar autoCut com tempo definido", () => {
    autoCut(10);
    expect(autoCut).toHaveBeenCalledWith(10);
  });
});
