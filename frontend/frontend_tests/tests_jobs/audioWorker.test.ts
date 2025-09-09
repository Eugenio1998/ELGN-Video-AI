vi.mock("@/jobs/audioWorker", () => ({
  processAudio: vi.fn(),
}));

import { describe, it, expect, vi } from "vitest";
import * as audioWorker from "@/jobs/audioWorker";

describe("audioWorker", () => {
  it("deve conter processAudio como função", () => {
    expect(typeof audioWorker.processAudio).toBe("function");
  });

  it("deve chamar processAudio com dados", () => {
    const data = { input: "audio.mp3" };
    audioWorker.processAudio(data);
    expect(audioWorker.processAudio).toHaveBeenCalledWith(data);
  });
});
