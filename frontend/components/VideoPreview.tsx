// 📂 components/VideoPreview.tsx
"use client";

import React from "react";
import { useTranslation } from "react-i18next";

interface VideoPreviewProps {
  videoUrl: string;
  className?: string;
}

export default function VideoPreview({
  videoUrl,
  className = "",
}: Readonly<VideoPreviewProps>) {
  const { t } = useTranslation();

  return (
    <div
      role="region"
      aria-label={t("preview.regionLabel")}
      className={`bg-[#0e0e0e] border border-[var(--color-border)] rounded-2xl shadow-lg w-full max-w-4xl mx-auto overflow-hidden ${className}`}
    >
      {/* Cabeçalho */}
      <div className="bg-[#181818] px-4 py-2 border-b border-zinc-700 text-sm text-[var(--color-accent)] font-semibold flex items-center gap-2">
        🎬 {t("preview.title")}
      </div>

      {/* Player */}
      <div className="bg-black flex justify-center items-center min-h-[240px]">
        {videoUrl ? (
          <video
            key={videoUrl}
            controls
            src={videoUrl}
            className="w-full aspect-video max-h-[600px] object-contain"
            aria-label={t("preview.ariaLabel")}
          />
        ) : (
          <div
            className="p-6 text-gray-400 text-sm"
            aria-live="polite"
            aria-busy="true"
          >
            🔄 {t("preview.loading")}
          </div>
        )}
      </div>
    </div>
  );
}
