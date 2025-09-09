// 📁 frontend_tests/tests_layouts/metadata.test.ts

import { describe, it, expect } from "vitest";
import { metadata } from "@/layouts/metadata";

describe("metadata config", () => {
  it("deve conter título e descrição", () => {
    expect(metadata.title).toBeDefined();
    expect(typeof metadata.title).toBe("string");

    expect(metadata.description).toBeDefined();
    expect(typeof metadata.description).toBe("string");
  });

  it("deve conter configurações de Open Graph válidas", () => {
    expect(metadata.openGraph).toBeDefined();
    expect(metadata.openGraph.title).toBeDefined();
    expect(metadata.openGraph.description).toBeDefined();
    expect(metadata.openGraph.images[0].url).toBeDefined();
  });

  it("deve conter configurações do Twitter válidas", () => {
    expect(metadata.twitter).toBeDefined();
    expect(metadata.twitter.title).toBeDefined();
    expect(metadata.twitter.description).toBeDefined();
    expect(metadata.twitter.image).toBeDefined();
  });
});
