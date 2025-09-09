// 📁 components/RequirePlan.tsx

import { ReactNode } from "react";
import { usePlan } from "@/hooks/usePlan";
import { PlanType } from "@/utils/planUtils";

type Props = {
  minPlan?: PlanType;
  children: ReactNode;
  fallback?: ReactNode;
};

const PLAN_ORDER: PlanType[] = [
  "basic",
  "pro",
  "premium",
  "enterprise",
  "admin",
];

export default function RequirePlan({
  minPlan = "basic",
  children,
  fallback = null,
}: Props) {
  const { plan } = usePlan(); // ✅ Corrigido: extrai apenas o plano (string)

  const hasAccess =
    PLAN_ORDER.indexOf(plan as PlanType) >= PLAN_ORDER.indexOf(minPlan) ||
    plan === "admin";

  return hasAccess ? <>{children}</> : <>{fallback}</>;
}
