// 📁 context/AppProviders.tsx
"use client";

import { ReactNode } from "react";
import { ThemeProvider } from "./ThemeProvider";
import { LanguageProvider } from "./LanguageProvider";
import { SessionProvider } from "./SessionProvider";
import { UIProvider } from "./UIContext";

// 🔁 Aplica todos os providers globais da aplicação
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <SessionProvider>
          <UIProvider>{children}</UIProvider>
        </SessionProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}
