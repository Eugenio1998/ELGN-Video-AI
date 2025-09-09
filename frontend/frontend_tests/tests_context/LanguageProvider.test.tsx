import { renderHook, act } from "@testing-library/react";
import { LanguageProvider, useLanguage } from "@/context/LanguageProvider";

describe("LanguageProvider", () => {
  it("deve fornecer o idioma atual e permitir mudança", () => {
    const { result } = renderHook(() => useLanguage(), {
      wrapper: ({ children }) => (
        <LanguageProvider>{children}</LanguageProvider>
      ),
    });

    expect(result.current.language).toBe("pt");

    act(() => {
      result.current.setLanguage("en");
    });

    expect(result.current.language).toBe("en");
  });
});
