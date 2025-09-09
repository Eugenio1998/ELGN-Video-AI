// 📁 pages/runway.tsx
"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { usePlan } from "../hooks/usePlan";
import { withAuth } from "../utils/withAuth";
import NavbarSimple from "@/components/NavbarSimple";

function RenderRunwayContent() {
  const { isFree, showPlanAlert } = usePlan();

  const [videoPrompt, setVideoPrompt] = useState("");
  const [audioPrompt, setAudioPrompt] = useState("");
  const [imagePrompt, setImagePrompt] = useState("");

  const [videoSize, setVideoSize] = useState("16:9");
  const [audioDuration, setAudioDuration] = useState(10);
  const [imageSize, setImageSize] = useState("1024x1024");

  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const [loadingVideo, setLoadingVideo] = useState(false);
  const [loadingAudio, setLoadingAudio] = useState(false);
  const [loadingImage, setLoadingImage] = useState(false);

  useEffect(() => {
    const plano = localStorage.getItem("plan") || "";
    if (!["basic", "basic anual"].includes(plano.toLowerCase())) {
      localStorage.removeItem("downloads");
    }
  }, []);

  const generate = async (
    type: "video" | "audio" | "image",
    prompt: string
  ) => {
    if (isFree) {
      showPlanAlert();
      return;
    }

    const plan = localStorage.getItem("plan") || "";
    const currentDownloads = parseInt(localStorage.getItem("downloads") || "0");

    if (["basic", "basic anual"].includes(plan.toLowerCase())) {
      if (currentDownloads >= 5) {
        alert("❌ Você atingiu o limite de 5 downloads no plano Basic.");
        window.location.href = "/plans";
        return;
      }
      localStorage.setItem("downloads", String(currentDownloads + 1));
    }

    const loadingSetter =
      type === "video"
        ? setLoadingVideo
        : type === "audio"
          ? setLoadingAudio
          : setLoadingImage;

    loadingSetter(true);

    const body =
      type === "video"
        ? { prompt, format: videoSize }
        : type === "audio"
          ? { prompt, duration: audioDuration }
          : { prompt, size: imageSize };

    const res = await fetch(`/api/${type}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    if (type === "video") setVideoUrl(data.video_url);
    if (type === "audio") setAudioUrl(data.url);
    if (type === "image") setImageUrl(data.image_url || data.url);

    loadingSetter(false);
  };

  const handleDownloadZip = async () => {
    const res = await fetch("/api/download-zip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        video: videoUrl,
        audio: audioUrl,
        image: imageUrl,
      }),
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "ia_resultado.zip";
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(url);
  };

  const handleReset = () => {
    setVideoPrompt("");
    setAudioPrompt("");
    setImagePrompt("");
    setVideoUrl(null);
    setAudioUrl(null);
    setImageUrl(null);
  };

  return (
    <div className="min-h-screen text-white relative overflow-auto">
      <div className="absolute inset-0 z-0 bg-[url('/img/Mario02.gif')] bg-cover bg-center bg-fixed" />
      <div className="absolute inset-0 bg-black/70 z-10" />
      <NavbarSimple />;
      <main className="relative z-10 px-4 py-6 h-full overflow-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 🧠 Coluna Esquerda - Criação */}
          <div className="space-y-6">
            <motion.h2
              className="text-2xl font-bold text-center"
              animate={{ color: ["#f97316", "#22c55e", "#3b82f6", "#ef4444"] }}
              transition={{ duration: 6, repeat: Infinity }}
            >
              🎮 Criador IA
            </motion.h2>

            {/* Vídeo */}
            <div className="bg-black/60 border border-blue-400 rounded-lg p-4">
              <label className="block font-medium mb-2">
                🎥 Prompt de Vídeo
              </label>
              <textarea
                value={videoPrompt}
                onChange={(e) => setVideoPrompt(e.target.value)}
                className="w-full bg-gray-800 p-2 rounded mb-2"
              />
              <select
                value={videoSize}
                onChange={(e) => setVideoSize(e.target.value)}
                className="w-full bg-gray-900 text-white rounded px-3 py-1 text-sm mb-2"
              >
                {["1:1", "4:3", "16:9", "21:9"].map((v) => (
                  <option key={v} value={v}>
                    Formato {v}
                  </option>
                ))}
              </select>
              <button
                onClick={() => {
                  if (isFree) {
                    showPlanAlert();
                    return;
                  }
                  generate("video", videoPrompt);
                }}
                disabled={loadingVideo}
                className={`w-full bg-blue-600 text-white py-1 rounded font-bold text-sm ${
                  loadingVideo ? "opacity-50 cursor-not-allowed" : ""
                }`}
              >
                {loadingVideo ? "⏳ Gerando..." : "🎬 Gerar Vídeo"}
              </button>
            </div>

            {/* Áudio */}
            <div className="bg-black/60 border border-pink-400 rounded-lg p-4">
              <label className="block font-medium mb-2">
                🎧 Prompt de Áudio
              </label>
              <textarea
                value={audioPrompt}
                onChange={(e) => setAudioPrompt(e.target.value)}
                className="w-full bg-gray-800 p-2 rounded mb-2"
              />
              <input
                type="number"
                min={1}
                max={120}
                value={audioDuration}
                onChange={(e) => setAudioDuration(Number(e.target.value))}
                className="w-full bg-gray-900 text-white rounded px-3 py-1 text-sm mb-2"
              />
              <button
                onClick={() => {
                  if (isFree) {
                    showPlanAlert();
                    return;
                  }
                  generate("audio", audioPrompt);
                }}
                disabled={loadingAudio}
                className="w-full bg-pink-500 text-white py-1 rounded font-bold text-sm"
              >
                {loadingAudio ? "⏳ Gerando..." : "🎵 Gerar Áudio"}
              </button>
            </div>

            {/* Imagem */}
            <div className="bg-black/60 border border-yellow-400 rounded-lg p-4">
              <label className="block font-medium mb-2">
                🖼️ Prompt de Imagem
              </label>
              <textarea
                value={imagePrompt}
                onChange={(e) => setImagePrompt(e.target.value)}
                className="w-full bg-gray-800 p-2 rounded mb-2"
              />
              <select
                value={imageSize}
                onChange={(e) => setImageSize(e.target.value)}
                className="w-full bg-gray-900 text-white rounded px-3 py-1 text-sm mb-2"
              >
                {["1024x1024", "1792x1024", "1024x1792", "512x512"].map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
              <button
                onClick={() => {
                  if (isFree) {
                    showPlanAlert();
                    return;
                  }
                  generate("image", imagePrompt);
                }}
                disabled={loadingImage}
                className="w-full bg-yellow-400 text-black py-1 rounded font-bold text-sm"
              >
                {loadingImage ? "⏳ Gerando..." : "🖌️ Gerar Imagem"}
              </button>
            </div>

            {/* Controles Finais */}
            <div className="bg-black/60 border border-white rounded-lg p-4">
              <button
                onClick={() => {
                  if (videoPrompt) generate("video", videoPrompt);
                  if (audioPrompt) generate("audio", audioPrompt);
                  if (imagePrompt) generate("image", imagePrompt);
                }}
                className="w-full mb-2 py-2 bg-gradient-to-r from-green-400 to-lime-500 text-black font-bold rounded"
              >
                ✨ Aplicar todos os prompts
              </button>
              <button
                onClick={handleReset}
                className="w-full text-sm text-gray-300 hover:underline"
              >
                🔁 Resetar tudo
              </button>
            </div>
          </div>

          {/* 🧪 Resultados */}
          <div className="space-y-6">
            <motion.h2
              className="text-2xl font-bold text-center"
              animate={{ color: ["#22c55e", "#3b82f6", "#ef4444", "#f97316"] }}
              transition={{ duration: 6, repeat: Infinity }}
            >
              🧪 Resultados IA
            </motion.h2>

            {videoUrl && (
              <div className="bg-black/60 border border-blue-500 rounded-lg p-4 space-y-3">
                <h3 className="text-blue-400 font-semibold">🎬 Vídeo</h3>
                <video controls src={videoUrl} className="w-full rounded" />
              </div>
            )}

            {audioUrl && (
              <div className="bg-black/60 border border-pink-400 rounded-lg p-4 space-y-3">
                <h3 className="text-pink-400 font-semibold">🎵 Áudio</h3>
                <audio controls src={audioUrl} className="w-full" />
              </div>
            )}

            {imageUrl && (
              <div className="bg-black/60 border border-yellow-400 rounded-lg p-4 space-y-3">
                <h3 className="text-yellow-400 font-semibold">🖼️ Imagem</h3>
                <Image
                  src={imageUrl}
                  alt="Imagem IA"
                  width={800}
                  height={800}
                  className="w-full rounded object-contain"
                />
              </div>
            )}

            {videoUrl && audioUrl && imageUrl && (
              <div className="bg-black/60 border border-lime-400 rounded-lg p-4 space-y-3">
                <h3 className="text-lime-400 font-semibold text-center">
                  🧩 Resultado Combinado
                </h3>
                <p className="text-sm text-gray-400 text-center">
                  Você gerou vídeo, áudio e imagem com IA.
                </p>
                <button
                  onClick={() => {
                    if (isFree) {
                      showPlanAlert();
                      return;
                    }
                    handleDownloadZip();
                  }}
                  className="w-full py-2 bg-gradient-to-r from-green-400 to-lime-500 text-black font-bold rounded"
                >
                  ⬇️ Download Tudo (ZIP)
                </button>
                <button
                  onClick={handleReset}
                  className="w-full text-xs text-gray-300 hover:underline text-center"
                >
                  🔁 Resetar Tudo
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function RunwayPage() {
  return <RenderRunwayContent />;
}

export default withAuth(RunwayPage);
