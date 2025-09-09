// 📁 utils/planUtils.ts

export type PlanType =
  | "free"
  | "basic"
  | "pro"
  | "premium"
  | "enterprise"
  | "admin";

export const isAdmin = (plan: PlanType) => plan === "admin";

export const isFree = (plan: PlanType) => plan === "free";

export const isBasic = (plan: PlanType) => ["free", "basic"].includes(plan);

export const isProOrAbove = (plan: PlanType) =>
  ["pro", "premium", "enterprise", "admin"].includes(plan);

export const isPremiumOrAbove = (plan: PlanType) =>
  ["premium", "enterprise", "admin"].includes(plan);
