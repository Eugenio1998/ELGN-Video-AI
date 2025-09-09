"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function NavbarSimple() {
  const router = useRouter();

  const handleBack = () => {
    router.back();
  };

  const handleDashboard = () => {
    router.push("/dashboard");
  };

  const handleLogout = () => {
    localStorage.clear();
    router.push("/login");
  };

  useEffect(() => {
    // Garantir que router esteja disponível
    if (!router) {
      console.warn("⚠️ Router não está disponível.");
    }
  }, [router]);

  return (
    <nav className="w-full bg-black/80 text-white px-6 py-4 flex justify-between items-center border-b border-gray-700 shadow-lg z-50 relative">
      <div className="flex gap-4">
        <button
          onClick={handleBack}
          className="px-3 py-1 rounded bg-gray-800 hover:bg-gray-700 text-sm transition"
        >
          🔙 Voltar
        </button>
        <button
          onClick={handleDashboard}
          className="px-3 py-1 rounded bg-blue-600 hover:bg-blue-500 text-sm transition"
        >
          🏠 Dashboard
        </button>
      </div>
      <button
        onClick={handleLogout}
        className="px-3 py-1 rounded bg-red-600 hover:bg-red-500 text-sm transition"
      >
        🚪 Sair
      </button>
    </nav>
  );
}
