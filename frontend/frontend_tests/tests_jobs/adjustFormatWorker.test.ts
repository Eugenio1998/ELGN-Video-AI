// frontend_tests/tests_jobs/adjustFormatWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/adjustFormatWorker", () => ({
  adjustFormat: vi.fn(),
}));

import { adjustFormat } from "@/jobs/adjustFormatWorker";

describe("adjustFormatWorker", () => {
  it("deve chamar adjustFormat com parâmetros", () => {
    adjustFormat("mp4");
    expect(adjustFormat).toHaveBeenCalledWith("mp4");
  });
});
