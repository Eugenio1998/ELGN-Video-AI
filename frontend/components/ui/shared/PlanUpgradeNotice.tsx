// 📁 components/ui/shared/PlanUpgradeNotice.tsx
"use client";

import Link from "next/link";
import { useTranslation } from "react-i18next";

interface PlanUpgradeNoticeProps {
  className?: string;
  showIcon?: boolean;
  align?: "left" | "center";
}

export function PlanUpgradeNotice({
  className = "",
  showIcon = true,
  align = "center",
}: PlanUpgradeNoticeProps) {
  const { t } = useTranslation();
  const alignmentClass = align === "center" ? "text-center" : "text-left";

  return (
    <div
      role="alert"
      aria-live="polite"
      className={`border border-yellow-500 bg-yellow-100/10 text-yellow-300 text-sm p-4 rounded-md ${alignmentClass} ${className}`}
    >
      {showIcon && "⚠️"} {t("plan.notice")}{" "}
      <Link
        href="/plans"
        className="underline text-yellow-200 hover:text-yellow-100"
      >
        {t("plan.link")}
      </Link>
    </div>
  );
}
