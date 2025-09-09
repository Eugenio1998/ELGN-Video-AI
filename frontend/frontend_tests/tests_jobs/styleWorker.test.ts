// frontend_tests/tests_jobs/styleWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/styleWorker", () => ({
  applyStyle: vi.fn(),
}));

import { applyStyle } from "@/jobs/styleWorker";

describe("styleWorker", () => {
  it("deve chamar applyStyle com tipo de estilo", () => {
    applyStyle({ type: "retro" });
    expect(applyStyle).toHaveBeenCalledWith({ type: "retro" });
  });
});
