"use client";

import { useState } from "react";

export default function AdminConfigPage() {
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  const toggleMaintenance = async () => {
    const newState = !maintenanceMode;
    setMaintenanceMode(newState);
    setStatusMessage("⏳ Atualizando configuração...");

    try {
      // ✅ Envie chamada real ao backend aqui futuramente
      // await fetch("/api/admin/maintenance", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ enabled: newState }),
      // });

      setStatusMessage(
        newState
          ? "🔴 Modo manutenção ativado."
          : "🟢 Modo manutenção desativado."
      );
    } catch {
      setStatusMessage("❌ Falha ao atualizar modo de manutenção.");
    }
  };

  return (
    <section className="p-8 max-w-4xl mx-auto text-white">
      <h1 className="text-2xl font-bold mb-6 text-[var(--color-accent)]">
        ⚙️ Configurações Gerais
      </h1>

      <div className="bg-black/50 border border-gray-700 rounded-xl p-6 space-y-6 shadow-lg">
        <div>
          <h2 className="text-lg font-semibold mb-2">🚧 Modo Manutenção</h2>
          <p className="text-sm mb-2 text-gray-400">
            Quando ativado, o sistema exibe uma página de manutenção para todos
            os usuários, exceto administradores.
          </p>

          <button
            onClick={toggleMaintenance}
            aria-pressed={maintenanceMode}
            aria-label="Alternar modo manutenção"
            className={`px-5 py-2 rounded-lg font-bold transition-colors duration-300 ${
              maintenanceMode
                ? "bg-red-600 hover:bg-red-700"
                : "bg-green-600 hover:bg-green-700"
            }`}
          >
            {maintenanceMode ? "Desativar" : "Ativar"}
          </button>

          {statusMessage && (
            <p className="mt-4 text-sm text-gray-300">{statusMessage}</p>
          )}
        </div>
      </div>
    </section>
  );
}
