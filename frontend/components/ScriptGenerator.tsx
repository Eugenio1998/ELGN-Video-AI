// 📂 components/ScriptGenerator.tsx
"use client";

import { useState } from "react";
import { FaMagic } from "react-icons/fa";
import { Textarea } from "../components/ui/textarea";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { useTranslation } from "react-i18next";

async function fetchScript(topic: string): Promise<string> {
  const res = await fetch("/api/generate-script", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic }),
  });

  if (!res.ok) throw new Error("API Error");

  const data = await res.json();
  return data.script ?? "";
}

export default function ScriptGenerator() {
  const { t } = useTranslation();
  const [topic, setTopic] = useState("");
  const [script, setScript] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const generateScript = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setScript("");

    try {
      const result = await fetchScript(topic);
      setScript(result || t("script.errorGenerate"));
    } catch (err) {
      console.error("Erro ao gerar roteiro:", err);
      setScript(t("script.errorServer"));
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(script);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="bg-gray-900 text-white p-6 rounded-xl border border-[var(--color-accent)] shadow-lg space-y-5">
      <h3 className="text-2xl font-bold text-[var(--color-accent)] flex items-center gap-2">
        <FaMagic className="text-lg" /> {t("script.title")}
      </h3>

      <div className="space-y-2">
        <Label htmlFor="topic">{t("script.topicLabel")}</Label>
        <Input
          id="topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder={t("script.topicPlaceholder")}
          className="bg-gray-800 text-white border-gray-700"
        />
      </div>

      <Button
        onClick={generateScript}
        disabled={loading}
        aria-busy={loading}
        aria-label={t("script.generateBtn")}
        className="mt-2"
      >
        {loading ? t("script.generating") : t("script.generateBtn")}
      </Button>

      {script && (
        <div className="space-y-2">
          <Label htmlFor="script">{t("script.resultLabel")}</Label>
          <Textarea
            id="script"
            value={script}
            readOnly
            className="h-40 resize-none bg-gray-800 border-gray-700 text-white"
            aria-live="polite"
          />
          <Button
            onClick={handleCopy}
            aria-label={t("script.copyBtn")}
            className="bg-green-500 hover:bg-green-600"
          >
            {copied ? t("script.copied") : t("script.copyBtn")}
          </Button>
        </div>
      )}
    </section>
  );
}
