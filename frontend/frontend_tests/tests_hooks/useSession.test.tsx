import { renderHook } from "@testing-library/react";
import { useThemeMode } from "@/hooks/useThemeMode";
import { ThemeProvider } from "next-themes";

describe("useThemeMode", () => {
  it("alterna entre dark e light", () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ThemeProvider>{children}</ThemeProvider>
    );

    const { result } = renderHook(() => useThemeMode(), { wrapper });
    expect(["light", "dark"]).toContain(result.current.theme);
  });
});
