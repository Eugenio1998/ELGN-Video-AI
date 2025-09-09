// 📁 hooks/useProtectedRoute.ts
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "../context/SessionProvider";

export function useProtectedRoute() {
  const { isLoggedIn } = useSession(); // ou useUser() se você quiser validar por token também
  const router = useRouter();

  useEffect(() => {
    // Protege rota somente após saber se está logado
    if (typeof window !== "undefined" && !isLoggedIn) {
      router.push("/login");
    }
  }, [isLoggedIn, router]);
}
