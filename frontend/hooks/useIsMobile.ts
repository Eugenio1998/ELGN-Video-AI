// 📁 hooks/useIsMobile.ts
import { useEffect, useState } from "react";

// ✅ Debounce simples sem dependência externa
function debounce(fn: () => void, delay: number) {
  let timeoutId: NodeJS.Timeout;
  return () => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(fn, delay);
  };
}

export function useIsMobile(breakpoint = 768, debounceDelay = 200) {
  const [isMobile, setIsMobile] = useState(() =>
    typeof window !== "undefined" ? window.innerWidth < breakpoint : false
  );

  useEffect(() => {
    if (typeof window === "undefined") return;

    const update = () => setIsMobile(window.innerWidth < breakpoint);
    const debouncedUpdate = debounce(update, debounceDelay);

    window.addEventListener("resize", debouncedUpdate);
    update(); // primeira verificação

    return () => window.removeEventListener("resize", debouncedUpdate);
  }, [breakpoint, debounceDelay]);

  return isMobile;
}
