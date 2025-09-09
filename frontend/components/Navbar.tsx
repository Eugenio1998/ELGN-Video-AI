// 📂 components/Navbar.tsx
"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import Cookies from "js-cookie";
import { useTranslation } from "react-i18next";
import { FaGlobeAmericas } from "react-icons/fa";

const languages = [
  { code: "pt-BR", label: "🇧🇷 PT-BR" },
  { code: "en-US", label: "🇺🇸 EN-US" },
  { code: "es", label: "🇪🇸 Español" },
  { code: "fr", label: "🇫🇷 Français" },
  { code: "de", label: "🇩🇪 Deutsch" },
  { code: "it", label: "🇮🇹 Italiano" },
  { code: "ru", label: "🇷🇺 Русский" },
  { code: "hi", label: "🇮🇳 हिंदी" },
  { code: "ar", label: "🇸🇦 العربية" },
  { code: "zh", label: "🇨🇳 中文" },
  { code: "ja", label: "🇯🇵 日本語" },
];

export default function Navbar() {
  const { t, i18n } = useTranslation();
  const [selectedLang, setSelectedLang] = useState(i18n.language || "pt-BR");

  useEffect(() => {
    const cookieLang = Cookies.get("i18next");
    if (cookieLang && cookieLang !== i18n.language) {
      i18n.changeLanguage(cookieLang);
      setSelectedLang(cookieLang);
    }
  }, [i18n]);

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const lang = e.target.value;
    Cookies.set("i18next", lang);
    setSelectedLang(lang);
    i18n.changeLanguage(lang);
  };

  return (
    <>
      <header>
        <nav
          role="navigation"
          className="bg-black text-white shadow-md flex justify-between items-center px-6 py-4 border-b border-white"
        >
          <Link href="/">
            <span className="cursor-pointer flex items-center gap-2">
              <Image
                src="/img/ELGN-AI.png"
                alt="ELGN Logo"
                width={100}
                height={40}
                className="object-contain"
              />
            </span>
          </Link>

          <div className="hidden md:flex space-x-6 items-center text-sm font-medium">
            <Link href="/login">
              <span className="hover:text-cyan-300">{t("Login")}</span>
            </Link>
            <Link href="/plans">
              <span className="hover:text-cyan-300">{t("Plans")}</span>
            </Link>

            <div className="flex items-center space-x-2">
              <FaGlobeAmericas className="text-xl text-white" />
              <select
                value={selectedLang}
                onChange={handleLanguageChange}
                className="bg-gray-800 border border-gray-600 text-white px-2 py-1 rounded"
                aria-label={t("navbar.language")}
              >
                {languages.map((lng) => (
                  <option key={lng.code} value={lng.code}>
                    {lng.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </nav>
      </header>

      {/* 🔆 Linha neon pulsante multicolorida abaixo do navbar */}
      <div className="h-[8px] w-full bg-gradient-to-r from-pink-500 via-yellow-300 to-cyan-400 animate-pulse blur-sm shadow-lg" />
    </>
  );
}
