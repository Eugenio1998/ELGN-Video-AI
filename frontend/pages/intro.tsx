// 📁 pages/intro.tsx

"use client";

import Link from "next/link";
import { motion } from "framer-motion";

export default function IntroPage() {
  return (
    <div className="relative min-h-screen bg-[url('/img/Mario.gif')] bg-cover bg-center bg-no-repeat bg-fixed px-4 py-12">
      {/* 🔳 Sombra escura no fundo */}
      <div className="absolute inset-0 bg-black/50 z-0" />

      {/* 🔲 Conteúdo acima da sombra */}
      <div className="relative z-10 flex items-center justify-center h-full">
        <div className="max-w-4xl w-full space-y-10 text-white text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold text-pink-400 drop-shadow-[0_0_15px_pink]">
            🚀 Bem-vindo ao ELGN Video.AI
          </h1>

          <p className="text-lg md:text-xl text-gray-300">
            Um editor de vídeos completo com Inteligência Artificial para
            criadores, empresas e equipes de marketing que buscam velocidade,
            qualidade e automação.
          </p>

          {/* 🌀 Card: Editor IA */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            whileHover={{ scale: 1.01, rotate: 0.3 }}
            className="bg-black/60 border border-cyan-400 rounded-xl p-6 shadow-md space-y-4 text-left"
          >
            <h2 className="text-2xl font-semibold text-cyan-300 drop-shadow-[0_0_8px_cyan]">
              📽️ Módulo de Edição com IA
            </h2>
            <p className="text-gray-200">
              Na aba <strong>Software</strong>, você pode transformar seus
              vídeos com:
            </p>
            <ul className="list-disc list-inside pl-4 space-y-1 text-gray-300">
              <li>✂️ Corte automático e remoção de silêncios.</li>
              <li>🎧 Melhoria de áudio com equalização inteligente.</li>
              <li>🔁 Compressão sem perda de qualidade.</li>
              <li>
                📐 Ajuste de resolução e proporção (TikTok, YouTube, etc).
              </li>
              <li>🎨 Filtros visuais personalizados ou automáticos via IA.</li>
              <li>🗣️ Geração de narração com voz neural.</li>
              <li>💬 Legendas automáticas multilíngue.</li>
              <li>🚀 SEO com IA: título, descrição, hashtags e tags.</li>
            </ul>
          </motion.div>

          {/* 🌀 Card: Geração IA */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            whileHover={{ scale: 1.01, rotate: 0.3 }}
            className="bg-black/60 border border-purple-400 rounded-xl p-6 shadow-md space-y-4 text-left"
          >
            <h2 className="text-2xl font-semibold text-purple-300 drop-shadow-[0_0_8px_purple]">
              🎬 Geração com IA
            </h2>
            <p className="text-gray-200">
              Na aba <strong>Gerador</strong>, você poderá:
            </p>
            <ul className="list-disc list-inside pl-4 space-y-1 text-gray-300">
              <li>🧠 Criar vídeos a partir de prompts com IA.</li>
              <li>
                🎶 Gerar áudios, músicas ou efeitos com base em descrição.
              </li>
              <li>🖼️ Criar imagens ilustrativas e thumbnails com IA visual.</li>
            </ul>
          </motion.div>

          {/* ✅ Botões */}
          <div className="text-center space-y-3">
            <p className="text-cyan-200 text-lg">
              Pronto para começar sua criação?
            </p>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col md:flex-row gap-6 justify-center mt-4"
            >
              <motion.div whileHover={{ scale: 1.05 }}>
                <Link
                  href="/software"
                  className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg rounded-xl shadow-lg transition-transform"
                >
                  🎬 Acessar Editor
                </Link>
              </motion.div>

              <motion.div whileHover={{ scale: 1.05 }}>
                <Link
                  href="/runway"
                  className="px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-bold text-lg rounded-xl shadow-lg transition-transform"
                >
                  🧠 Ir para Gerador
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
