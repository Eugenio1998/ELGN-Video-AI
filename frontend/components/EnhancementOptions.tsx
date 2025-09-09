// 📂 components/EnhancementOptions.tsx
"use client";

import { ChangeEvent } from "react";
import { useTranslation } from "react-i18next";

interface EnhancementOptionsProps {
  values: {
    upscale: boolean;
    stabilize: boolean;
    colorFix: boolean;
    crop: boolean;
  };
  onChange: (
    name: keyof EnhancementOptionsProps["values"],
    value: boolean
  ) => void;
  disabled?: boolean;
  className?: string;
}

export const enhancementLabels: Record<
  keyof EnhancementOptionsProps["values"],
  string
> = {
  upscale: "video.upscale",
  stabilize: "video.stabilize",
  colorFix: "video.colorFix",
  crop: "video.crop",
};

export default function EnhancementOptions({
  values,
  onChange,
  disabled = false,
  className = "",
}: EnhancementOptionsProps) {
  const { t } = useTranslation();

  return (
    <fieldset
      className={`bg-gray-900 p-4 rounded-2xl border border-[var(--color-accent)] shadow-md space-y-4 ${className}`}
      aria-labelledby="enhancement-legend"
      disabled={disabled}
    >
      <legend
        id="enhancement-legend"
        className="text-xl font-bold text-[var(--color-accent)] mb-2"
      >
        ⚙️ {t("video.enhancements")}
      </legend>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {Object.entries(enhancementLabels).map(([key, translationKey]) => (
          <label
            key={key}
            className="flex items-center space-x-3 text-sm cursor-pointer hover:text-white transition"
          >
            <input
              type="checkbox"
              checked={values[key as keyof EnhancementOptionsProps["values"]]}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                onChange(
                  key as keyof EnhancementOptionsProps["values"],
                  e.target.checked
                )
              }
              className="accent-[var(--color-accent)] w-4 h-4 focus:ring-2 focus:ring-[var(--color-accent)]"
              aria-label={t(translationKey)}
              disabled={disabled}
            />
            <span>{t(translationKey)}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
