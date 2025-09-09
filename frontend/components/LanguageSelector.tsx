// 📂 components/LanguageSelector.tsx
"use client";

import { useTranslation } from "react-i18next";
import { useEffect, useState } from "react";

const languages = [
  { code: "pt-BR", label: "Português (Brasil)", emoji: "🇧🇷" },
  { code: "en-US", label: "Inglês (EUA)", emoji: "🇺🇸" },
  { code: "es", label: "Espanhol", emoji: "🇪🇸" },
  { code: "fr", label: "Francês", emoji: "🇫🇷" },
  { code: "de", label: "Alemão", emoji: "🇩🇪" },
  { code: "it", label: "Italiano", emoji: "🇮🇹" },
  { code: "ru", label: "Russo", emoji: "🇷🇺" },
  { code: "hi", label: "Hindi", emoji: "🇮🇳" },
  { code: "ar", label: "Árabe", emoji: "🇸🇦" },
  { code: "zh", label: "Chinês", emoji: "🇨🇳" },
  { code: "ja", label: "Japonês", emoji: "🇯🇵" },
];

export default function LanguageSelector() {
  const { i18n, t } = useTranslation();
  const [lang, setLang] = useState(i18n.language || "pt-BR");

  const handleLanguageChange = (value: string) => {
    setLang(value);
    i18n.changeLanguage(value);
    document.cookie = `i18next=${value}; path=/`;
  };

  useEffect(() => {
    const stored = i18n.language;
    if (stored) setLang(stored);
  }, [i18n.language]);

  return (
    <div className="mb-4">
      <label
        htmlFor="language-select"
        className="block text-sm font-medium mb-1"
      >
        {t("video.languageLabel")}
      </label>
      <select
        id="language-select"
        aria-label={t("video.languageLabel")}
        value={lang}
        onChange={(e) => handleLanguageChange(e.target.value)}
        className="bg-gray-800 border border-gray-600 text-white px-4 py-2 rounded"
      >
        {languages.map((lng) => (
          <option key={lng.code} value={lng.code}>
            {lng.emoji} {lng.label}
          </option>
        ))}
      </select>
    </div>
  );
}
