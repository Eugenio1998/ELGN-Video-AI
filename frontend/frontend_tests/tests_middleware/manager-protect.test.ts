import { describe, it, expect } from "vitest";
import { requireManager } from "@/middleware/manager-protect";

describe("managerProtect middleware", () => {
  it("should be a function", () => {
    expect(typeof requireManager).toBe("function");
  });
});
