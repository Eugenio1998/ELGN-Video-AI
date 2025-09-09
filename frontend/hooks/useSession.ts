// 📁 hooks/useSession.ts

// ✅ Atalho para usar sessão sem importar diretamente do contexto
import { useSession as useSessionContext } from "../context/SessionProvider";

export function useSession() {
  const { isLoggedIn, userPlan, hasAccess, setSession } = useSessionContext();
  return { isLoggedIn, userPlan, hasAccess, setSession };
}
