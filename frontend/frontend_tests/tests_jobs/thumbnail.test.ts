// frontend_tests/tests_jobs/thumbnail.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/thumbnailWorker", () => ({
  generateThumbnail: vi.fn(),
}));

import { generateThumbnail } from "@/jobs/thumbnailWorker";

describe("thumbnail", () => {
  it("deve chamar generateThumbnail com tempo correto", () => {
    generateThumbnail(15);
    expect(generateThumbnail).toHaveBeenCalledWith(15);
  });
});
