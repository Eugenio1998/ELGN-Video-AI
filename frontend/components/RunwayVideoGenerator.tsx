// 📂 components/RunwayVideoGenerator.tsx
"use client";

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";

async function generateVideo(
  prompt: string,
  duration: number,
  seed: number
): Promise<string | null> {
  const formData = new FormData();
  formData.append("prompt", prompt);
  formData.append("duration", duration.toString());
  formData.append("seed", seed.toString());

  const response = await fetch("/api/runway-video", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) throw new Error("Falha na geração do vídeo");

  const data = await response.json();
  return data.video_url ?? null;
}

export default function RunwayVideoGenerator() {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState("");
  const [duration, setDuration] = useState(4);
  const [seed, setSeed] = useState(42);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError(t("video.promptRequired"));
      return;
    }

    setLoading(true);
    setVideoUrl(null);
    setError("");

    try {
      const url = await generateVideo(prompt, duration, seed);
      if (url) {
        setVideoUrl(url);
      } else {
        setError(t("video.generationFailed"));
      }
    } catch (err) {
      console.error("Erro ao gerar vídeo:", err);
      setError(t("video.internalError"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="bg-gray-900 text-white p-6 rounded-xl border border-[var(--color-accent)] shadow-xl space-y-5">
      <h2 className="text-2xl font-bold">🎥 {t("video.title")}</h2>

      <div className="space-y-2">
        <Label htmlFor="prompt">{t("video.promptLabel")}</Label>
        <Textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={t("video.promptPlaceholder")}
          className="bg-gray-800 text-white border-gray-600"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="duration">⏱️ {t("video.durationLabel")}</Label>
          <Input
            id="duration"
            type="number"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            min={1}
            max={10}
            className="bg-gray-800 text-white border-gray-600"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="seed">🔁 {t("video.seedLabel")}</Label>
          <Input
            id="seed"
            type="number"
            value={seed}
            onChange={(e) => setSeed(Number(e.target.value))}
            className="bg-gray-800 text-white border-gray-600"
          />
        </div>
      </div>

      {error && (
        <p className="text-red-400 text-sm" aria-live="assertive">
          {error}
        </p>
      )}

      <Button
        onClick={handleGenerate}
        disabled={loading}
        aria-busy={loading}
        aria-label={t("video.generateBtn")}
        className="mt-2"
      >
        {loading ? t("video.generating") : t("video.generateBtn")}
      </Button>

      {videoUrl && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2">🎬 {t("video.result")}</h3>
          <video
            src={videoUrl}
            controls
            className="rounded-lg w-full max-w-3xl border border-gray-700"
          />
        </div>
      )}
    </section>
  );
}
