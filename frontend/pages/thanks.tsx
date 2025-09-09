// 📁 pages/thanks.tsx

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { FaCheckCircle } from "react-icons/fa";
import { withAuth } from "../utils/withAuth";

function RenderThanksContent() {
  const router = useRouter();
  const [plano, setPlano] = useState<string>("");

  useEffect(() => {
    // ✅ Libera o acesso ao software
    localStorage.setItem("userStatus", "ativo");

    // ✅ Busca o plano salvo localmente
    const savedPlan = localStorage.getItem("plan");
    setPlano(savedPlan ? savedPlan.toUpperCase() : "DESCONHECIDO");

    // ✅ Redirecionamento automático em 10s
    const timeout = setTimeout(() => {
      router.push("/dashboard");
    }, 10000);

    return () => clearTimeout(timeout);
  }, [router]);

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[url('/img/Mario02.gif')] bg-cover bg-center bg-no-repeat bg-fixed px-4 py-16 text-white">
      {/* 🔳 Sombra e fundo escurecido */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/40 to-black/60 z-0" />

      {/* 🟩 Card de confirmação */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 max-w-md w-full p-8 rounded-xl border-2 border-lime-400 shadow-lg bg-black/80 backdrop-blur-lg text-center"
      >
        {/* Efeito neon pulsante */}
        <div className="absolute -inset-1 rounded-xl border-2 border-lime-400 blur-[2px] opacity-40 animate-pulse pointer-events-none" />

        <FaCheckCircle className="text-lime-400 text-6xl mb-4 drop-shadow-[0_0_10px_lime]" />
        <h1 className="text-3xl font-bold mb-3 drop-shadow">
          Pagamento Confirmado!
        </h1>

        <p className="text-green-300 text-sm mb-2">
          Plano ativado: <span className="uppercase font-bold">{plano}</span>
        </p>

        <p className="text-gray-300 mb-6 text-sm">
          Sua assinatura foi ativada com sucesso. Agora você tem acesso completo
          ao editor inteligente e aos recursos premium do ELGN Video.AI.
        </p>

        <motion.div whileHover={{ scale: 1.03 }}>
          <Link
            href="/dashboard"
            className="inline-block px-6 py-3 bg-gradient-to-r from-green-500 to-lime-500 text-black font-semibold rounded-lg hover:brightness-110 transition"
          >
            Ir para a IA
          </Link>
        </motion.div>

        <p className="text-xs text-gray-400 mt-4">
          Você será redirecionado automaticamente em 10 segundos...
        </p>
      </motion.div>
    </div>
  );
}

function ThanksPage() {
  return <RenderThanksContent />;
}

export default withAuth(ThanksPage);
