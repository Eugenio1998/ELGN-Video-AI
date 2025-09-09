// frontend_tests/tests_jobs/queue.test.ts
import { describe, it, expect, vi } from "vitest";

vi.mock("@/jobs/queue", () => ({
  enqueue: vi.fn(),
}));

import { enqueue } from "@/jobs/queue";

describe("queue", () => {
  it("deve chamar enqueue com job de teste", () => {
    enqueue({ type: "test", payload: {} });
    expect(enqueue).toHaveBeenCalledWith({ type: "test", payload: {} });
  });
});
