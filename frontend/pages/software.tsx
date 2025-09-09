"use client";

import { useState } from "react";
import UploadVideo from "../components/UploadVideo";
import VideoPreview from "../components/VideoPreview";
import { motion } from "framer-motion";
import { withAuth } from "../utils/withAuth";
import NavbarSimple from "@/components/NavbarSimple";
import { usePlan } from "../hooks/usePlan";
import { useDownloadLimit } from "@/hooks/useDownloadLimit";

function RenderSoftwareContent() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [musicFile, setMusicFile] = useState<File | null>(null);
  const [processedVideoUrl, setProcessedVideoUrl] = useState<string | null>(
    null
  );

  const [loading, setLoading] = useState(false);
  const { isFree, hasAccessToCreation, showPlanAlert } = usePlan();

  const { canDownload, registerDownload } = useDownloadLimit("video");

  const [enhancements, setEnhancements] = useState({
    upscale: false,
    stabilize: false,
    colorFix: false,
    crop: false,
    music: false,
    audioEdit: false,
    subtitles: false,
  });

  const [seoData, setSeoData] = useState({
    title: "",
    description: "",
    tags: "",
    copyright: "",
    scriptPrompt: "",
  });

  const [resolution, setResolution] = useState("1080p");
  const [aspectRatio, setAspectRatio] = useState("16:9");
  const [seoPrompt, setSeoPrompt] = useState("");
  const [selectedFormat, setSelectedFormat] = useState<string>("mp4");
  const [selectedFilter, setSelectedFilter] = useState<string>("none");
  const [seoLanguage, setSeoLanguage] = useState("pt");

  const selectedButtonClass =
    "bg-cyan-400 text-black shadow-md shadow-cyan-300";
  const unselectedButtonClass = "bg-gray-800 text-white hover:bg-gray-700";

  // ✅ Aplicar IA no vídeo
  const handleApply = async () => {
    if (!videoFile) {
      alert("Envie um vídeo para aplicar a IA.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", videoFile);
      if (enhancements.music && musicFile) {
        formData.append("music", musicFile);
      }

      const uploadResponse = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadResponse.json();
      const jobId = uploadData.jobId;
      if (!jobId) throw new Error("Job ID não retornado.");

      if (enhancements.crop) {
        await fetch("/api/apply-cuts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ jobId }),
        });
      }

      if (enhancements.colorFix) {
        await fetch("/api/apply-filters", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ jobId, filters: ["warm", "cinematic"] }),
        });
      }

      if (enhancements.audioEdit) {
        await fetch("/api/apply-voice", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ jobId, voice: "nova" }),
        });
      }

      await fetch("/api/apply-resolution", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobId, resolution }),
      });

      await fetch("/api/adjust-format", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobId, targetFormat: aspectRatio }),
      });

      await fetch("/api/compress-video", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobId, targetSizeMb: 50 }),
      });

      await fetch("/api/generate-thumbnail", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobId }),
      });

      const finalizeResponse = await fetch("/api/finalize-export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jobId }),
      });

      const finalizeData = await finalizeResponse.json();
      const finalUrl = finalizeData.downloadUrl || "/mock-final-video.mp4";

      setProcessedVideoUrl(finalUrl);

      // Salvar histórico
      await fetch("/api/history", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: "video",
          url: finalUrl,
          prompt: seoPrompt,
        }),
      });

      alert("✅ Vídeo finalizado e salvo no histórico!");
    } catch (error: unknown) {
      if (error instanceof Error) {
        console.error("❌ Erro no processamento:", error);
        alert("Erro: " + error.message);
      } else {
        console.error("❌ Erro desconhecido:", error);
        alert("Erro inesperado. Veja o console.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSEO = async () => {
    if (!seoPrompt.trim()) {
      alert("❌ Escreva um tópico para gerar o SEO.");
      return;
    }

    try {
      const response = await fetch("/api/generate-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: seoPrompt, language: seoLanguage }),
      });

      const data = await response.json();

      if (data.error) {
        alert("❌ Erro ao gerar SEO.");
        return;
      }

      setSeoData((prev) => ({
        ...prev,
        title: data.title,
        tags: data.tags,
        description: data.description,
      }));

      alert("✅ SEO gerado com sucesso!");
    } catch (error) {
      console.error("Erro:", error);
      alert("Erro ao gerar SEO.");
    }
  };

  const handleReset = () => {
    setVideoFile(null);
    setProcessedVideoUrl(null);
    setSeoPrompt("");
    setSeoData({
      title: "",
      description: "",
      tags: "",
      copyright: "",
      scriptPrompt: "",
    });
    setEnhancements({
      upscale: false,
      stabilize: false,
      colorFix: false,
      crop: false,
      music: false,
      audioEdit: false,
      subtitles: false,
    });
  };

  return (
    <div className="min-h-screen flex flex-col text-white relative">
      {/* Plano de fundo */}
      <div
        className="absolute inset-0 z-0"
        aria-hidden="true"
        style={{
          backgroundImage: "url('/img/Mario.gif')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundAttachment: "fixed",
        }}
      />
      {/* Camada de sombreamento */}
      <div className="absolute inset-0 z-10 bg-gradient-to-b from-black/50 via-black/50 to-black/50" />

      <NavbarSimple />

      {/* Conteúdo principal */}
      <main className="relative z-10 px-4 py-6 h-full overflow-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Coluna Esquerda - Upload + Config */}
          <div className="space-y-4">
            <motion.h2
              className="text-xl font-bold text-center neon-text mb-4"
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
              🎥 Vídeo Original
            </motion.h2>

            <UploadVideo
              onUploadComplete={(data) => {
                console.log("✅ Upload completo no software:", data);
                // Ex: salvar no estado, mostrar preview, preencher campos
                // setVideoData(data);
              }}
            />

            <div className="p-4 space-y-4 bg-black/60 backdrop-blur-md rounded-lg border border-white">
              {/* Resolução e proporção */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-medium mb-1">Resolução</label>
                  <select
                    aria-label="Selecionar resolução"
                    className="bg-gray-800 text-white px-3 py-2 rounded w-full"
                    value={resolution}
                    onChange={(e) => setResolution(e.target.value)}
                  >
                    <option value="720p">720p</option>
                    <option value="1080p">1080p</option>
                    <option value="1440p">1440p</option>
                    <option value="2k">2K</option>
                    <option value="4k">4K</option>
                    <option value="8k">8K</option>
                  </select>
                </div>
                <div>
                  <label className="block font-medium mb-1">Proporção</label>
                  <select
                    aria-label="Selecionar proporção"
                    className="bg-gray-800 text-white px-3 py-2 rounded w-full"
                    value={aspectRatio}
                    onChange={(e) => setAspectRatio(e.target.value)}
                  >
                    <option value="1:1">1:1</option>
                    <option value="4:3">4:3</option>
                    <option value="16:9">16:9</option>
                    <option value="21:9">21:9</option>
                  </select>
                </div>
              </div>

              {/* Aprimoramentos IA */}
              <div>
                <label className="block font-medium mb-2 mt-2">
                  Aprimoramentos e Recursos
                </label>
                <div
                  className="grid grid-cols-1 gap-2"
                  role="group"
                  aria-label="Aprimoramentos IA"
                >
                  {Object.entries(enhancements).map(([key, value]) => (
                    <button
                      key={key}
                      onClick={() =>
                        setEnhancements((prev) => ({
                          ...prev,
                          [key]: !prev[key as keyof typeof enhancements],
                        }))
                      }
                      className={`text-left text-sm px-3 py-2 rounded transition duration-300 ${
                        value ? selectedButtonClass : unselectedButtonClass
                      }`}
                    >
                      {key === "upscale" && "🔍 Melhoria de Resolução"}
                      {key === "stabilize" && "📹 Estabilização"}
                      {key === "colorFix" && "🎨 Correção de Cor"}
                      {key === "crop" && "✂️ Corte Inteligente"}
                      {key === "music" && "🎵 Música de Fundo"}
                      {key === "audioEdit" && "🎚️ Edição de Áudio"}
                      {key === "subtitles" && "📝 Legendas Automáticas"}
                      {key === "runwayVideo" &&
                        "🎬 Geração de Vídeo IA (Runway)"}
                      {key === "runwayAudio" &&
                        "🎶 Geração de Áudio IA (Runway)"}
                      {key === "resetJob" && "♻️ Resetar Edição"}
                    </button>
                  ))}
                </div>
              </div>

              {/* Filtros IA */}
              <div className="mt-4">
                <label className="block font-medium mb-2">🎛️ Filtros IA</label>
                <div
                  className="grid grid-cols-1 gap-2"
                  role="radiogroup"
                  aria-label="Filtros IA"
                >
                  {[
                    "none",
                    "bw",
                    "vintage",
                    "anime",
                    "cartoon",
                    "glow",
                    "cinematic",
                  ].map((filter) => (
                    <button
                      key={filter}
                      onClick={() => setSelectedFilter(filter)}
                      className={`text-left text-sm px-3 py-2 rounded transition duration-300 ${
                        selectedFilter === filter
                          ? selectedButtonClass
                          : unselectedButtonClass
                      }`}
                    >
                      {filter === "none" && "🚫 Nenhum"}
                      {filter === "bw" && "⚫ Branco e Preto"}
                      {filter === "vintage" && "📽️ Vintage"}
                      {filter === "anime" && "🌀 Estilo Anime"}
                      {filter === "cartoon" && "🎨 Cartoon"}
                      {filter === "glow" && "✨ Glow/Neon"}
                      {filter === "cinematic" && "🎬 Cinemático"}
                    </button>
                  ))}
                </div>
              </div>

              {/* Upload de música */}
              <div>
                <label className="block font-medium mb-2">
                  🎵 Música de Fundo (opcional)
                </label>
                <input
                  type="file"
                  accept="audio/*"
                  className="bg-gray-800 text-white px-3 py-2 rounded w-full"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      setMusicFile(file);
                    }
                  }}
                />

                {musicFile && (
                  <div className="mt-2 space-y-2">
                    <audio
                      controls
                      src={URL.createObjectURL(musicFile)}
                      className="w-full"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => setMusicFile(null)}
                        className="text-xs text-red-400 hover:underline"
                      >
                        ❌ Remover Música
                      </button>
                      <label className="text-xs text-blue-400 hover:underline cursor-pointer">
                        📁 Substituir
                        <input
                          type="file"
                          accept="audio/*"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              setMusicFile(file);
                            }
                          }}
                        />
                      </label>
                    </div>
                  </div>
                )}
              </div>

              {/* SEO Prompt e Geração */}
              <div className="mt-4">
                <label className="block text-sm font-medium mb-1">
                  ✍️ Gerar SEO
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-2">
                  <input
                    type="text"
                    value={seoPrompt}
                    onChange={(e) => setSeoPrompt(e.target.value)}
                    placeholder="Digite o tema do vídeo"
                    className="bg-gray-800 text-white px-3 py-2 rounded w-full"
                    aria-label="Prompt de SEO"
                  />
                  <select
                    value={seoLanguage}
                    onChange={(e) => setSeoLanguage(e.target.value)}
                    className="bg-gray-800 text-white px-3 py-2 rounded w-full"
                    aria-label="Idioma do SEO"
                  >
                    <option value="pt">🇧🇷 Português</option>
                    <option value="en">🇺🇸 English</option>
                    <option value="es">🇪🇸 Español</option>
                    <option value="fr">🇫🇷 Français</option>
                    <option value="de">🇩🇪 Deutsch</option>
                    <option value="ja">🇯🇵 日本語</option>
                    <option value="zh">🇨🇳 中文</option>
                    <option value="hi">🇮🇳 Hindi</option>
                  </select>
                </div>

                <button
                  onClick={handleGenerateSEO}
                  className="w-full py-2 text-sm bg-gradient-to-r from-yellow-400 via-orange-400 to-red-500 text-white font-bold rounded shadow hover:scale-105 transition-transform duration-300"
                >
                  🚀 Gerar SEO com IA
                </button>
              </div>
            </div>

            {/* Ações finais */}
            <div className="p-4 bg-black/60 backdrop-blur-md rounded-lg border border-white space-y-3 mt-4">
              <h3 className="text-lg font-semibold text-center">
                🎯 Ações Finais
              </h3>

              <button
                onClick={() => {
                  if (!hasAccessToCreation) {
                    showPlanAlert();
                    return;
                  }
                  handleApply();
                }}
                aria-label="Aplicar IA ao vídeo"
                className="w-full py-2 text-sm bg-gradient-to-r from-blue-500 via-indigo-400 to-purple-500 text-white font-bold rounded shadow hover:scale-105 transition-transform duration-300"
              >
                {loading ? "⏳ Processando..." : "⚡ Aplicar IA"}
              </button>

              <button
                onClick={handleReset}
                aria-label="Resetar edição"
                className="w-full py-2 text-white font-bold rounded shadow hover:brightness-110"
              >
                🔄 Resetar Edição
              </button>
            </div>
          </div>

          {/* Coluna Direita - Resultado IA */}
          <div className="space-y-4">
            <motion.h2
              className="text-xl font-bold text-center neon-text mb-4"
              animate={{
                color: [
                  "#22c55e",
                  "#eab308",
                  "#3b82f6",
                  "#ef4444",
                  "#ec4899",
                  "#f97316",
                ],
              }}
              transition={{ duration: 6, repeat: Infinity }}
            >
              🧠 Resultado da IA
            </motion.h2>

            <div className="p-4 bg-black/60 backdrop-blur-md rounded-lg border border-white space-y-4">
              <div>
                <h3 className="text-lg font-semibold">🎯 Título Gerado:</h3>
                <p className="bg-gray-800 px-3 py-2 rounded mt-1">
                  {seoData.title || "Nenhum título gerado ainda."}
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold">🏷️ Tags:</h3>
                <p className="bg-gray-800 px-3 py-2 rounded mt-1">
                  {seoData.tags || "Nenhuma tag gerada ainda."}
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold">📝 Descrição:</h3>
                <p className="bg-gray-800 px-3 py-2 rounded mt-1">
                  {seoData.description || "Nenhuma descrição gerada ainda."}
                </p>
              </div>
            </div>

            {/* Preview e download do vídeo final */}
            {processedVideoUrl && (
              <div className="p-4 bg-black/60 backdrop-blur-md rounded-lg border border-white space-y-4">
                <h3 className="text-lg font-semibold text-white">
                  📽️ Vídeo Gerado
                </h3>
                <VideoPreview videoUrl={processedVideoUrl} />

                <div className="space-y-2">
                  <h4 className="text-sm font-semibold text-white">
                    💾 Escolha o formato:
                  </h4>
                  <div className="space-y-1">
                    {["mp4", "mov", "webm"].map((format) => (
                      <label
                        key={format}
                        className="flex items-center space-x-2 text-white text-sm"
                      >
                        <input
                          type="radio"
                          name="videoFormat"
                          value={format}
                          checked={selectedFormat === format}
                          onChange={() => setSelectedFormat(format)}
                          className="accent-green-400"
                        />
                        <span>{format.toUpperCase()}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="pt-4">
                  <button
                    onClick={() => {
                      if (isFree) {
                        alert(
                          "🔒 O plano Free não permite baixar vídeos. Faça upgrade."
                        );
                        return;
                      }

                      if (!canDownload) {
                        alert(
                          "❌ Limite de downloads atingido. Faça upgrade para continuar."
                        );
                        return;
                      }

                      registerDownload();

                      if (processedVideoUrl && selectedFormat) {
                        const link = document.createElement("a");
                        link.href = processedVideoUrl;
                        link.download = `video-elgn.${selectedFormat}`;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                      }
                    }}
                    className="w-full py-2 text-sm bg-gradient-to-r from-green-400 to-lime-500 text-black font-bold rounded shadow hover:scale-105 transition-transform duration-300"
                    aria-label="Baixar vídeo no formato selecionado"
                  >
                    ⬇️ Baixar Vídeo
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>{" "}
        {/* Fecha grid-cols */}
      </main>
    </div>
  );
}

function SoftwarePage() {
  return <RenderSoftwareContent />;
}

export default withAuth(SoftwarePage);
