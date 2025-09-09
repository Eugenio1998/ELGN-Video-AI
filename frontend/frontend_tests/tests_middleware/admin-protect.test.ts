import { describe, it, expect } from "vitest";
import { requireAdmin } from "@/middleware/admin-protect";

describe("adminProtect middleware", () => {
  it("should be a function", () => {
    expect(typeof requireAdmin).toBe("function");
  });
});
