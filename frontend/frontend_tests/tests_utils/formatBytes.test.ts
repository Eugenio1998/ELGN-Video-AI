import { formatBytes } from "@/utils/formatBytes";

describe("formatBytes", () => {
  it("should be defined", () => {
    expect(formatBytes).toBeDefined();
  });

  it("should format bytes correctly", () => {
    expect(formatBytes(1024)).toMatch(/KB/);
    expect(formatBytes(1048576)).toMatch(/MB/);
  });
});