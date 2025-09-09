// frontend_tests/tests_jobs/compressionWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/compressionWorker", () => ({
  compress: vi.fn(),
}));

import { compress } from "@/jobs/compressionWorker";

describe("compressionWorker", () => {
  it("deve chamar compress com qualidade correta", () => {
    compress(80);
    expect(compress).toHaveBeenCalledWith(80);
  });
});
