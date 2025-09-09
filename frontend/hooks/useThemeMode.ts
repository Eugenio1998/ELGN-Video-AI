// 📁 hooks/useThemeMode.ts
import { useTheme } from "../context/ThemeProvider";

export function useThemeMode() {
  const { theme, changeTheme } = useTheme();
  const toggleTheme = () => changeTheme(theme === "dark" ? "light" : "dark");

  return { theme, toggleTheme, changeTheme };
}
