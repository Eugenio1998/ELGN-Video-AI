// 📁 components/ui/shared/ThemeToggle.tsx
"use client";

import { useEffect, useState } from "react";
import { Switch } from "./Switch";
import { useTranslation } from "react-i18next";

interface ThemeToggleProps {
  className?: string;
}

export function ThemeToggle({ className = "" }: ThemeToggleProps) {
  const { t } = useTranslation();
  const [darkMode, setDarkMode] = useState(true);

  // Aplicar a classe no primeiro load (evita flicker)
  useEffect(() => {
    const saved = localStorage.getItem("theme");
    const isDark = saved !== "light";
    setDarkMode(isDark);
    document.documentElement.classList.toggle("dark", isDark);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  return (
    <div className={`mt-2 ${className}`} aria-label={t("theme.ariaLabel")}>
      <Switch
        enabled={darkMode}
        onToggle={setDarkMode}
        label={darkMode ? t("theme.dark") : t("theme.light")}
      />
    </div>
  );
}
