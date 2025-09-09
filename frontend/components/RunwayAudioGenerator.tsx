// 📂 components/RunwayAudioGenerator.tsx
"use client";

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";

const audioStyles = [
  "ambient",
  "cinematic",
  "pop",
  "lo-fi",
  "rock",
  "jazz",
  "electronic",
];

async function generateAudio(
  prompt: string,
  style: string
): Promise<string | null> {
  const formData = new FormData();
  formData.append("prompt", prompt);
  formData.append("style", style);

  const response = await fetch("/api/runway-audio", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) throw new Error("Failed to generate");

  const data = await response.json();
  return data.audio_url ?? null;
}

export default function RunwayAudioGenerator() {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState("");
  const [style, setStyle] = useState("ambient");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError(t("audio.promptRequired"));
      return;
    }

    setLoading(true);
    setAudioUrl(null);
    setError("");

    try {
      const url = await generateAudio(prompt, style);
      if (url) {
        setAudioUrl(url);
      } else {
        setError(t("audio.generationFailed"));
      }
    } catch (err) {
      console.error("Erro ao gerar áudio:", err);
      setError(t("audio.internalError"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="bg-gray-900 text-white p-6 rounded-xl border border-[var(--color-accent)] shadow-xl space-y-5">
      <h2 className="text-2xl font-bold">🎧 {t("audio.title")}</h2>

      <div className="space-y-2">
        <Label htmlFor="prompt">{t("audio.promptLabel")}</Label>
        <Textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={t("audio.promptPlaceholder")}
          className="bg-gray-800 text-white border-gray-600"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="style">{t("audio.styleLabel")}</Label>
        <select
          id="style"
          value={style}
          onChange={(e) => setStyle(e.target.value)}
          className="bg-gray-800 text-white border border-gray-600 px-4 py-2 rounded"
        >
          {audioStyles.map((s) => (
            <option key={s} value={s}>
              🎵 {s}
            </option>
          ))}
        </select>
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
        aria-label={t("audio.generateBtn")}
        className="mt-2"
      >
        {loading ? t("audio.generating") : t("audio.generateBtn")}
      </Button>

      {audioUrl && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-2">🔊 {t("audio.result")}</h3>
          <audio
            src={audioUrl}
            controls
            className="w-full max-w-2xl rounded border border-gray-700"
          />
        </div>
      )}
    </section>
  );
}
