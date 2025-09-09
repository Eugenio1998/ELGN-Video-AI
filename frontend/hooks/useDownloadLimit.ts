// 📁 hooks/useDownloadLimit.ts
import { useEffect, useState } from "react";
import { usePlan } from "./usePlan";

export function useDownloadLimit(type: "video" | "audio" | "image" = "video") {
  const { plan, isFree, showPlanAlert } = usePlan();

  // Limite apenas para planos básicos
  const limit = ["basic", "basic anual"].includes(plan) ? 5 : Infinity;

  const storageKey = `downloadCount_${type}`;
  const [count, setCount] = useState(() => {
    const saved = localStorage.getItem(storageKey);
    return saved ? Number(saved) : 0;
  });

  useEffect(() => {
    localStorage.setItem(storageKey, String(count));
  }, [count, storageKey]);

  const canDownload = () => {
    if (isFree) {
      showPlanAlert();
      return false;
    }

    if (limit !== Infinity && count >= limit) {
      alert(
        `❌ Você atingiu o limite de ${limit} downloads no plano Basic. Faça upgrade.`
      );
      window.location.href = "/plans";
      return false;
    }

    return true;
  };

  const registerDownload = () => {
    if (canDownload()) {
      setCount((prev) => prev + 1);
    }
  };

  const resetDownloadCount = () => setCount(0);

  return {
    count,
    canDownload,
    registerDownload,
    resetDownloadCount,
    isFree,
    plan,
  };
}
