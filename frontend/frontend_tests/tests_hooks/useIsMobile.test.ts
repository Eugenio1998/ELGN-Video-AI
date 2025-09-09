import { renderHook } from "@testing-library/react";
import { useIsMobile } from "@/hooks/useIsMobile";

describe("useIsMobile", () => {
  it("deve retornar true se largura da tela for menor que 768px", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: 500,
    });

    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(true);
  });

  it("deve retornar false se largura da tela for maior que 768px", () => {
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: 1024,
    });

    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);
  });
});
