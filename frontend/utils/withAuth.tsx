// 📁 utils/withAuth.tsx

"use client";

import { useEffect, useState } from "react";

export function withAuth<T extends Record<string, unknown>>(
  Component: React.ComponentType<T>
) {
  return function ProtectedComponent(props: T) {
    const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);

    useEffect(() => {
      const token = localStorage.getItem("token");

      if (process.env.NEXT_PUBLIC_DISABLE_AUTH === "true") {
        console.warn(
          "⚠️ withAuth: modo de autenticação está desabilitado (dev)"
        );
        setIsAuthorized(true);
        return;
      }

      if (token) {
        setIsAuthorized(true);
      } else {
        setIsAuthorized(false);
      }
    }, []);

    if (isAuthorized === null) {
      return (
        <div className="text-white text-center py-10">
          🔐 Verificando autorização...
        </div>
      );
    }

    if (!isAuthorized) {
      window.location.href = "/login";
      return null;
    }

    return <Component {...props} />;
  };
}
