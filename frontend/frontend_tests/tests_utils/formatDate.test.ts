import { formatDate } from "@/utils/formatDate";

describe("formatDate", () => {
  it("should be defined", () => {
    expect(formatDate).toBeDefined();
  });

  it("should format a valid date", () => {
    const result = formatDate("2025-01-01");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });
});