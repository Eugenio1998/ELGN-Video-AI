// 📁 hooks/usePlan.tsx
import { useUser } from "../context/UserContext";
import { useUI } from "../context/UIContext";

export function usePlan() {
  const { user } = useUser();
  const { showToast } = useUI();

  // ✅ Corrigido para considerar "ADMIN" ou "admin"
  const isAdmin = user?.role?.toLowerCase() === "admin";
  const plan = isAdmin
    ? "admin"
    : (user?.normalizedPlan || "free").toLowerCase();

  const isFree = plan === "free";
  const isPro = plan.includes("pro");
  const isPremium = plan.includes("premium");
  const isEnterprise = plan.includes("empresarial");

  const hasAccessToDownload = !isFree || isAdmin;
  const hasAccessToCreation = isPro || isPremium || isEnterprise || isAdmin;

  const showPlanAlert = () => {
    const confirmed = window.confirm(
      "⚠️ Este recurso é exclusivo para usuários com plano ativo.\n\nDeseja ver os planos disponíveis?"
    );
    if (confirmed) {
      window.location.href = "/plans";
    } else {
      showToast?.("Você pode atualizar seu plano a qualquer momento.", "info");
    }
  };

  console.log("🔎 Plano:", plan, "| Role:", user?.role);

  return {
    plan,
    isFree,
    isPro,
    isPremium,
    isEnterprise,
    hasAccessToDownload,
    hasAccessToCreation,
    showPlanAlert,
  };
}
