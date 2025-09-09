// 📂 components/VideoEditorTest.tsx
"use client";

import { useState, useEffect, ChangeEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FaMagic } from "react-icons/fa";
import { useTranslation } from "react-i18next";
import { usePlan } from "../hooks/usePlan";

export default function VideoEditorTest() {
  const { t } = useTranslation();
  const router = useRouter();
  const { isFree } = usePlan();

  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith("video/")) {
      setVideoFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setSuccess(false);
    }
  };

  const simulateProcessing = () => {
    setProcessing(true);
    setSuccess(false);
    setTimeout(() => {
      setProcessing(false);
      setSuccess(true);
    }, 2000);
  };

  const handleBlockedFeature = () => {
    alert(t("test.blocked"));
    router.push("/plans");
  };

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  return (
    <section className="bg-gray-900 text-white p-6 rounded-xl border border-[var(--color-accent)] shadow-xl w-full max-w-4xl mx-auto mt-10 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[var(--color-accent)] mb-1 flex items-center gap-2">
          <FaMagic /> {t("test.title")}
        </h2>
        <p className="text-sm text-gray-400">{t("test.subtitle")}</p>
      </div>

      <input
        type="file"
        accept="video/*"
        onChange={handleUpload}
        className="file:border file:px-4 file:py-2 file:rounded-md file:cursor-pointer bg-gray-800 border border-gray-700 text-sm w-full"
        aria-label={t("test.uploadLabel")}
      />

      {previewUrl && (
        <video
          src={previewUrl}
          controls
          className="w-full h-auto rounded-md border border-[var(--color-accent)] shadow-md"
        />
      )}

      <button
        onClick={isFree ? simulateProcessing : handleBlockedFeature}
        disabled={!videoFile || processing}
        className="bg-[var(--color-accent)] hover:bg-opacity-80 text-black font-semibold px-6 py-2 rounded-md transition disabled:opacity-50"
        aria-busy={processing}
        aria-label={t("test.simulateBtn")}
      >
        {processing ? t("test.processing") : t("test.simulateBtn")}
      </button>

      {success && (
        <p className="text-green-400 text-sm" aria-live="polite">
          ✅ {t("test.successMessage")}
        </p>
      )}

      <p className="text-sm text-gray-400">
        {t("test.cta")}{" "}
        <Link
          href="/plans"
          className="underline text-[var(--color-secondary)] hover:text-white"
        >
          {t("test.plans")}
        </Link>
        .
      </p>
    </section>
  );
}
