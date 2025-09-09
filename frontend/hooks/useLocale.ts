// 📁 hooks/useLocale.ts
import { useTranslation } from "react-i18next";
import { useLanguage } from "../context/LanguageProvider";
import { useEffect } from "react";

export function useLocale() {
  const { t, i18n } = useTranslation();
  const { language, setLanguage } = useLanguage();

  // 🔁 Sincroniza context e i18n
  useEffect(() => {
    if (language !== i18n.language) {
      i18n.changeLanguage(language);
    }
  }, [language, i18n]);

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
    setLanguage(lang);
  };

  return {
    t,
    currentLanguage: i18n.language,
    changeLanguage,
  };
}
