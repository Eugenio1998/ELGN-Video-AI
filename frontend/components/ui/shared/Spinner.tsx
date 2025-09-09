// 📁 components/ui/shared/Spinner.tsx
"use client";

import { useTranslation } from "react-i18next";
import clsx from "clsx";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  colorClass?: string;
}

export function Spinner({
  size = "md",
  className = "",
  colorClass = "border-2 border-white/40 border-t-white",
}: SpinnerProps) {
  const { t } = useTranslation();

  const sizeClass = {
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-8 h-8",
  };

  return (
    <div
      className={clsx(
        colorClass,
        "animate-spin rounded-full",
        sizeClass[size],
        className
      )}
      role="status"
      aria-label={t("loading.processing")}
    />
  );
}
