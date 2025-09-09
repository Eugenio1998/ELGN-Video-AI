import { describe, it, expect } from "vitest";
import { requireUser } from "@/middleware/user-protect";

describe("userProtect middleware", () => {
  it("should be a function", () => {
    expect(typeof requireUser).toBe("function");
  });
});
