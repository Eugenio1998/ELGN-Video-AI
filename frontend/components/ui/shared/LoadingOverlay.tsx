// 📂 components/ui/shared/LoadingOverlay.tsx
"use client";

import { Spinner } from "./Spinner";
import { useTranslation } from "react-i18next";

interface LoadingOverlayProps {
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ message }) => {
  const { t } = useTranslation();
  const text = message || t("loading.processing");

  return (
    <div
      className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
      role="alert"
      aria-live="assertive"
      aria-label={text}
      aria-busy="true"
    >
      <div className="flex items-center" role="status">
        <Spinner />
        <span className="ml-3 text-white text-sm">{text}</span>
      </div>
    </div>
  );
};
