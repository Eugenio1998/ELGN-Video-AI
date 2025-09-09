// 📁 pages/plans.tsx

"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function PlanosPage() {
  const router = useRouter();
  const [planoAtivo, setPlanoAtivo] = useState<string | null>(null);

  useEffect(() => {
    const plano = localStorage.getItem("plan");
    setPlanoAtivo(plano);
  }, []);

  const handleAssinar = (plano: string) => {
    router.push(`/checkout?plano=${encodeURIComponent(plano)}`);
  };

  const planos = [
    {
      nome: "Basic",
      preco: "$10",
      descricao: "Acesso limitado a recursos do editor IA.",
      categoria: "mensal",
      recursos: [
        "Resolução até 1440p",
        "Proporção TikTok e Shorts",
        "Filtros",
        "Sem criador de conteúdo",
        "Sem armazenamento em nuvem",
      ],
    },
    {
      nome: "Pro",
      preco: "$25",
      descricao: "Acesso ampliado ao editor + criador IA + nuvem.",
      categoria: "mensal",
      recursos: [
        "Resolução até 2K",
        "Legendas Automáticas",
        "Melhoria de Imagens com IA",
        "Acesso ao criador IA de conteúdo",
        "100GB de armazenamento em nuvem",
      ],
    },
    {
      nome: "Premium",
      preco: "$50",
      descricao: "Todos os recursos liberados + nuvem turbinada.",
      categoria: "mensal",
      recursos: [
        "Todos os recursos do editor de vídeo com IA",
        "Todos os recursos do criador IA",
        "500GB de armazenamento em nuvem",
      ],
    },
    {
      nome: "Empresarial",
      preco: "$100",
      descricao: "Performance máxima para equipes e empresas.",
      categoria: "mensal",
      recursos: [
        "Editor e criador IA completos",
        "1TB de armazenamento em nuvem",
        "Suporte dedicado",
      ],
    },
    {
      nome: "Basic Anual",
      preco: "$100",
      descricao: "Plano básico com pagamento anual.",
      categoria: "anual",
      recursos: [
        "Resolução até 1440p",
        "Proporção TikTok e Shorts",
        "Filtros",
        "Sem criador de conteúdo",
        "Sem armazenamento em nuvem",
      ],
    },
    {
      nome: "Pro Anual",
      preco: "$250",
      descricao: "Plano Pro com desconto e dobro de nuvem.",
      categoria: "anual",
      recursos: [
        "Resolução até 2K",
        "Legendas Automáticas",
        "Melhoria de Imagens com IA",
        "Acesso ao criador IA",
        "200GB de armazenamento em nuvem",
        "Pagamento em até 12x sem juros",
      ],
    },
    {
      nome: "Premium Anual",
      preco: "$500",
      descricao: "Todos os recursos e 1TB de nuvem.",
      categoria: "anual",
      recursos: [
        "Todos os recursos do Pro",
        "Editor + Criador IA completos",
        "1TB de armazenamento em nuvem",
        "Pagamento em até 12x sem juros",
      ],
    },
    {
      nome: "Empresarial Anual",
      preco: "$1000",
      descricao: "Recursos avançados e escalabilidade total.",
      categoria: "anual",
      recursos: [
        "Editor e criador IA ilimitados",
        "2TB de armazenamento em nuvem",
        "SLA, APIs e suporte dedicado",
        "Pagamento em até 12x sem juros",
      ],
    },
  ];

  const corBorda = (nome: string) => {
    if (["Basic", "Basic Anual"].includes(nome)) return "white";
    if (["Pro", "Pro Anual"].includes(nome)) return "blue-400";
    if (["Premium", "Premium Anual"].includes(nome)) return "fuchsia-500";
    return "orange-400";
  };

  const renderCards = (categoria: string) =>
    planos
      .filter((plano) => plano.categoria === categoria)
      .map((plano, idx) => {
        const cor = corBorda(plano.nome);

        const borderClass =
          cor === "white"
            ? "border-white hover:shadow-white"
            : cor === "blue-400"
              ? "border-blue-400 hover:shadow-blue-400"
              : cor === "fuchsia-500"
                ? "border-fuchsia-500 hover:shadow-fuchsia-500"
                : "border-orange-400 hover:shadow-orange-400";

        const pulseClass =
          cor === "white"
            ? "border-white"
            : cor === "blue-400"
              ? "border-blue-400"
              : cor === "fuchsia-500"
                ? "border-fuchsia-500"
                : "border-orange-400";

        const isAtivo = plano.nome.toLowerCase() === planoAtivo?.toLowerCase();

        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: idx * 0.1 }}
            whileHover={{ scale: 1.04, rotate: 0.3 }}
            className={`relative border-2 rounded-xl p-6 bg-black ${borderClass} shadow-md transition-all duration-300`}
          >
            <div
              className={`absolute -inset-1 rounded-xl border-2 ${pulseClass} blur-[3px] opacity-50 animate-pulse pointer-events-none`}
            ></div>

            <div className="relative z-10">
              <h2 className="text-xl font-bold text-white mb-2 flex justify-between items-center">
                {plano.nome}
                {isAtivo && (
                  <span className="text-xs bg-lime-500 text-black font-bold px-2 py-1 rounded ml-2">
                    ✔ Plano Atual
                  </span>
                )}
              </h2>
              <p className="text-sm text-gray-300 mb-4">{plano.descricao}</p>
              <p className="text-2xl font-bold text-lime-400 mb-4">
                {plano.preco}
              </p>
              <ul className="text-sm list-disc list-inside text-gray-200 space-y-1 mb-6">
                {plano.recursos.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={() => handleAssinar(plano.nome)}
                disabled={isAtivo}
                className={`w-full py-2 font-bold rounded transition duration-300 ${
                  isAtivo
                    ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                    : "bg-gradient-to-r from-green-400 to-lime-500 text-black hover:brightness-110"
                }`}
              >
                {isAtivo ? "Seu plano atual" : "Assinar"}
              </motion.button>
            </div>
          </motion.div>
        );
      });

  return (
    <div className="relative min-h-screen bg-black text-white">
      <div className="absolute inset-0 bg-[url('/img/Mario02.gif')] bg-cover bg-center bg-no-repeat bg-fixed z-0" />
      <div className="absolute inset-0 bg-black/50 z-0" />

      <div className="relative z-10 px-4 py-12">
        <motion.h1
          className="text-4xl font-extrabold text-center text-lime-300 drop-shadow-[0_0_15px_lime] mb-12"
          animate={{ opacity: [0, 1] }}
          transition={{ duration: 1 }}
        >
          💼 Planos de Assinatura ELGN Video.AI
        </motion.h1>

        <h2 className="text-2xl font-bold text-white mb-6">
          🗕️ Planos Mensais
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-12">
          {renderCards("mensal")}
        </div>

        <h2 className="text-2xl font-bold text-white mb-6">🗖 Planos Anuais</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {renderCards("anual")}
        </div>
      </div>
    </div>
  );
}
