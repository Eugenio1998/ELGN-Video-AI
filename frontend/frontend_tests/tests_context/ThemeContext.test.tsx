import { renderHook, act } from "@testing-library/react";
import { ThemeProvider } from "@/context/ThemeContext";
import { useTheme } from "@/context/ThemeContext";

describe("ThemeContext", () => {
  it("deve alternar entre light e dark", () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: ({ children }) => <ThemeProvider>{children}</ThemeProvider>,
    });

    const initialTheme = result.current.theme;

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.theme).not.toBe(initialTheme);
    expect(["light", "dark"]).toContain(result.current.theme);
  });
});
