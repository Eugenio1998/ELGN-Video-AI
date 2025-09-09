// frontend_tests/tests_jobs/exportWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/exportWorker", () => ({
  exportFinalVideo: vi.fn(),
}));

import { exportFinalVideo } from "@/jobs/exportWorker";

describe("exportWorker", () => {
  it("deve chamar exportFinalVideo com nome de arquivo", () => {
    exportFinalVideo("meu_video_final.mp4");
    expect(exportFinalVideo).toHaveBeenCalledWith("meu_video_final.mp4");
  });
});
