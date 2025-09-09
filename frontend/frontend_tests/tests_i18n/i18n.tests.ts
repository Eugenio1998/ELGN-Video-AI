// frontend_tests/i18n/i18n.test.ts
import i18n from "@/i18n/i18n";
import { describe, it, expect } from "vitest";

describe("i18n", () => {
  it("deve estar inicializado", () => {
    expect(i18n.isInitialized).toBe(true);
  });

  it("deve ter 'pt' como idioma padrão", () => {
    expect(i18n.options.fallbackLng).toBe("pt");
  });

  it("deve suportar múltiplos idiomas", () => {
    const supported = i18n.options.supportedLngs;
    expect(supported).toContain("pt");
    expect(supported).toContain("en");
    expect(supported).toContain("es");
    expect(supported).toContain("fr");
    expect(supported).toContain("de");
    expect(supported).toContain("ru");
    expect(supported).toContain("hi");
    expect(supported).toContain("ar");
    expect(supported).toContain("zh");
    expect(supported).toContain("ja");
  });
});
