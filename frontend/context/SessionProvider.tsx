// 📁 context/SessionProvider.tsx
"use client";

import {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect,
} from "react";

// 🔐 Tipos possíveis de plano (pronto para expansão futura)
export type PlanType = "free" | "basic" | "pro" | "premium" | "enterprise";

interface SessionContextType {
  isLoggedIn: boolean;
  userPlan: PlanType;
  hasAccess: boolean; // true somente se usuário estiver logado e com plano pago
  setSession: (data: { isLoggedIn: boolean; userPlan: PlanType }) => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const SessionProvider = ({ children }: { children: ReactNode }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userPlan, setUserPlan] = useState<PlanType>("free");

  useEffect(() => {
    // 🔁 Carrega sessão do localStorage na primeira montagem
    const auth = localStorage.getItem("auth") === "true";
    const plan = (localStorage.getItem("plan") as PlanType) || "free";
    setIsLoggedIn(auth);
    setUserPlan(plan);
  }, []);

  const setSession = ({
    isLoggedIn,
    userPlan,
  }: {
    isLoggedIn: boolean;
    userPlan: PlanType;
  }) => {
    localStorage.setItem("auth", String(isLoggedIn));
    localStorage.setItem("plan", userPlan);
    setIsLoggedIn(isLoggedIn);
    setUserPlan(userPlan);

    // 🔁 Atualiza dados do usuário automaticamente
    if (typeof window !== "undefined") {
      const event = new Event("refreshUser");
      window.dispatchEvent(event);
    }
  };

  // ✅ Apenas usuários logados e com plano pago têm acesso completo
  const hasAccess = isLoggedIn && userPlan !== "free";

  return (
    <SessionContext.Provider
      value={{
        isLoggedIn,
        userPlan,
        hasAccess,
        setSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = (): SessionContextType => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error("useSession deve ser usado dentro de <SessionProvider>");
  }
  return context;
};
