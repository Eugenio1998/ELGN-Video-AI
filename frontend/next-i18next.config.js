// 📁 next-i18next.config.js

module.exports = {
  i18n: {
    defaultLocale: "pt",
    locales: ["pt", "en", "es", "fr", "de", "ru", "hi", "ar", "zh", "ja"],
    localeDetection: true,
  },
  reloadOnPrerender: process.env.NODE_ENV === "development",
  fallbackLng: "pt",
};
