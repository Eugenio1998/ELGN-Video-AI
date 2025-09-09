// 📁 pages/checkout.tsx

"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function CheckoutPage() {
  const router = useRouter();
  const [plano, setPlano] = useState("");

  const colorMap: Record<string, string> = {
    Basic: "white",
    "Basic Anual": "white",
    Pro: "blue-400",
    "Pro Anual": "blue-400",
    Premium: "fuchsia-500",
    "Premium Anual": "fuchsia-500",
    Empresarial: "orange-400",
    "Empresarial Anual": "orange-400",
  };

  const cor = colorMap[plano] || "gray-500";

  const borderClass = `border-${cor} hover:shadow-${cor}`;
  const pulseClass = `border-${cor}`;
  const textClass = `text-${cor}`;

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const planoSelecionado = params.get("plano");
    if (planoSelecionado) {
      setPlano(planoSelecionado);
    } else {
      router.push("/plans");
    }
  }, [router]);

  const handleContinuar = () => {
    if (!plano || !(plano in colorMap)) {
      alert("Erro: Plano não encontrado.");
      router.push("/plans");
      return;
    }

    localStorage.setItem("plan", plano);
    router.push(`/payment?plano=${encodeURIComponent(plano)}`);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[url('/img/Mario02.gif')] bg-cover bg-center bg-no-repeat bg-fixed px-4 py-12">
      {/* Camada escurecida */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/30 to-black/50 z-0" />

      {/* Card central */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className={`relative z-10 max-w-md w-full p-6 rounded-xl border-2 ${borderClass} shadow-lg bg-black/80 backdrop-blur-lg`}
      >
        <div
          className={`absolute -inset-1 rounded-xl border-2 ${pulseClass} blur-[2px] opacity-40 animate-pulse pointer-events-none`}
        />

        <h1 className="text-2xl font-bold text-center mb-4 text-white drop-shadow">
          🧾 Confirmação de Assinatura
        </h1>

        <p className="text-center text-gray-300 mb-6">
          Você escolheu o plano:
          <br />
          <span className={`${textClass} font-bold text-lg`}>{plano}</span>
        </p>

        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={handleContinuar}
          aria-label="Continuar para pagamento"
          className="w-full py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold rounded hover:brightness-110 transition-transform"
        >
          Continuar para Pagamento
        </motion.button>

        <button
          onClick={() => router.push("/plans")}
          aria-label="Voltar para os planos"
          className="w-full py-2 mt-4 text-sm text-gray-400 hover:text-white hover:underline transition"
        >
          ← Voltar aos Planos
        </button>
      </motion.div>
    </div>
  );
}
