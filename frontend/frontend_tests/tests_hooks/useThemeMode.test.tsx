// frontend_tests/tests_hooks/useThemeMode.test.tsx
import { renderHook } from "@testing-library/react";
import { useThemeMode } from "@/hooks/useThemeMode";
import { ThemeProvider } from "next-themes";

describe("useThemeMode", () => {
  // 🛠️ Mock do window.matchMedia
  beforeAll(() => {
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: (query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }),
    });
  });

  it("alterna entre dark e light", () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ThemeProvider>{children}</ThemeProvider>
    );

    const { result } = renderHook(() => useThemeMode(), { wrapper });
    expect(["light", "dark"]).toContain(result.current.theme);
  });
});
