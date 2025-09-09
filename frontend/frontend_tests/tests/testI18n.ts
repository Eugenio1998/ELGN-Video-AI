// 📁 frontend/lib/testI18n.ts
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

void i18n.use(initReactI18next).init({
  lng: "en",
  fallbackLng: "en",
  resources: {
    en: { translation: { hello: "Hello" } },
    pt: { translation: { hello: "Olá" } },
  },
  interpolation: { escapeValue: false },
});

export default i18n;
