// frontend_tests/tests_jobs/addMusicWorker.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/addMusicWorker", () => ({
  addMusicToVideo: vi.fn(),
}));

import { addMusicToVideo } from "@/jobs/addMusicWorker";

describe("addMusicWorker", () => {
  it("deve chamar addMusicToVideo com música e volume", () => {
    addMusicToVideo("trilha.mp3", 0.7);
    expect(addMusicToVideo).toHaveBeenCalledWith("trilha.mp3", 0.7);
  });
});
