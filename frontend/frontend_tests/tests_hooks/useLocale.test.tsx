// frontend_tests/tests_hooks/useLocale.test.tsx
import { renderHook } from "@testing-library/react";
import { I18nextProvider } from "react-i18next";
import i18n from "../tests/testI18n";
import { LanguageProvider } from "@/context/LanguageProvider";
import { useLocale } from "@/hooks/useLocale";

describe("useLocale", () => {
  it("deve conter função de tradução", () => {
    const { result } = renderHook(() => useLocale(), {
      wrapper: ({ children }) => (
        <I18nextProvider i18n={i18n}>
          <LanguageProvider>{children}</LanguageProvider>
        </I18nextProvider>
      ),
    });

    expect(result.current.t).toBeInstanceOf(Function);
  });

  it("deve alterar o idioma corretamente", async () => {
    const { result } = renderHook(() => useLocale(), {
      wrapper: ({ children }) => (
        <I18nextProvider i18n={i18n}>
          <LanguageProvider>{children}</LanguageProvider>
        </I18nextProvider>
      ),
    });

    await result.current.changeLanguage("en");
    expect(result.current.currentLanguage).toBe("en");
  });
});
