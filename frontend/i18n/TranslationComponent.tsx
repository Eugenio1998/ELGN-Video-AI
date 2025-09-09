// components/__tests__/TranslationComponent.tsx
"use client";

import { useTranslation } from "react-i18next";

export default function TranslationComponent() {
  const { t } = useTranslation();
  return <div>{t("hello")}</div>;
}
