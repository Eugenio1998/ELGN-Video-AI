// 📁 pages/index.tsx

"use client";

import { useTranslation } from "react-i18next";
import Head from "next/head";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";

const Home = () => {
  const {} = useTranslation();

  const features = [
    {
      title: "🎬 Edição Automática de Vídeo",
      description:
        "Corte de silêncios, melhoria de imagem, ajuste de proporção, detecção de cenas, compressão e filtros visuais com inteligência artificial.",
    },
    {
      title: "🎤 Narração e Áudio com IA",
      description:
        "Geração de voz realista por texto, equalização, remoção de ruído e sincronização automática com o vídeo.",
    },
    {
      title: "📝 Legendas e SEO Inteligente",
      description:
        "Transcrição automática com Whisper AI, geração de títulos, tags e descrições otimizadas para YouTube, Instagram e outras plataformas.",
    },
    {
      title: "🧠 Criação de Conteúdo com IA",
      description:
        "Geração de vídeos e áudios do zero com IA, além de roteiros completos e adaptação para redes sociais.",
    },
  ];

  return (
    <>
      <Head>
        <title>ELGN Video AI</title>
      </Head>

      <main className="min-h-screen bg-[url('/img/Mario.gif')] bg-cover bg-center bg-no-repeat bg-fixed text-white relative">
        {/* 🔳 Camada escurecedora com blur para efeito 3D */}
        <div className="absolute inset-0 bg-black/70 z-0" />
        <div className="relative z-10">
          {/* 🚀 Seção inicial */}
          <section className="text-center py-16 px-6">
            <motion.div className="flex justify-center mb-6">
              <Image
                src="/img/ELGN-AI.png"
                alt="ELGN Logo"
                width={200}
                height={60}
                className="object-contain"
              />
            </motion.div>

            <motion.h1
              className="text-4xl md:text-5xl font-bold mb-6 neon-text"
              animate={{
                color: [
                  "#f97316",
                  "#22c55e",
                  "#eab308",
                  "#3b82f6",
                  "#ef4444",
                  "#ec4899",
                ],
              }}
              transition={{ duration: 6, repeat: Infinity }}
            >
              ELGN Video AI
            </motion.h1>

            <p className="max-w-3xl mx-auto text-lg md:text-xl text-gray-300">
              Uma plataforma de edição de vídeo com inteligência artificial que
              automatiza tudo: cortes, filtros, áudio, legenda, SEO e até
              criação completa de conteúdo com IA.
            </p>

            {/* 🎥 Vídeo com borda pulsante */}
            <div className="relative rounded-2xl overflow-hidden max-w-3xl mx-auto mt-10">
              <div className="pointer-events-none absolute -inset-1 rounded-2xl border-2 border-white opacity-40 blur-md animate-pulse" />
              <video
                className="w-full rounded-2xl border-2 border-white"
                controls
                src="/video/apresentacao.mp4"
              />
            </div>
          </section>

          {/* 🎯 Funcionalidades */}
          <section className="py-20 px-6">
            <motion.h2
              className="text-3xl md:text-4xl font-bold text-center mb-12 neon-text"
              animate={{
                color: [
                  "#f97316",
                  "#22c55e",
                  "#eab308",
                  "#3b82f6",
                  "#ef4444",
                  "#ec4899",
                ],
              }}
              transition={{ duration: 6, repeat: Infinity }}
            >
              Tudo o que o ELGN Video AI faz por você
            </motion.h2>

            <div className="grid gap-10 sm:grid-cols-1 md:grid-cols-2 xl:grid-cols-4 max-w-7xl mx-auto">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  className="bg-black text-white p-8 rounded-2xl relative overflow-hidden shadow-xl border border-gray-700 min-h-[340px] flex flex-col justify-between"
                  animate={{
                    boxShadow: [
                      "0 0 10px #f97316",
                      "0 0 10px #22c55e",
                      "0 0 10px #eab308",
                      "0 0 10px #3b82f6",
                      "0 0 10px #ef4444",
                      "0 0 10px #ec4899",
                    ],
                  }}
                  transition={{ duration: 5, repeat: Infinity }}
                >
                  <h3 className="text-2xl font-bold mb-4 leading-snug">
                    {feature.title}
                  </h3>
                  <p className="text-gray-300 text-base leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </div>

            {/* 🚀 Botão de chamada para ação */}
            <div className="text-center mt-12">
              <Link href="/intro">
                <button className="mt-4 bg-gradient-to-r from-green-400 to-blue-500 hover:brightness-110 px-8 py-4 text-white font-semibold text-lg rounded-xl shadow-xl">
                  🚀 Testar Agora o Editor Inteligente
                </button>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </>
  );
};

export default dynamic(() => Promise.resolve(Home), { ssr: false });
