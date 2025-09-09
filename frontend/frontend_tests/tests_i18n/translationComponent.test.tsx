// frontend_tests/i18n/translationComponent.test.tsx
import { render, screen } from "@testing-library/react";
import TranslationComponent from "@/i18n/TranslationComponent";
import i18n from "@/i18n/i18n";
import { I18nextProvider } from "react-i18next";
import { describe, it, expect, beforeAll } from "vitest";

describe("TranslationComponent", () => {
  beforeAll(() => {
    i18n.init({
      lng: "en",
      fallbackLng: "en",
      debug: false,
      resources: {
        en: {
          translation: {
            hello: "Hello World!",
          },
        },
      },
    });
  });

  it("deve exibir a tradução correta da chave 'hello'", () => {
    render(
      <I18nextProvider i18n={i18n}>
        <TranslationComponent />
      </I18nextProvider>
    );

    expect(screen.getByText("Hello World!")).toBeInTheDocument();
  });
});
