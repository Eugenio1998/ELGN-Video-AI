// 📁 components/UploadVideo.tsx
"use client";

import { useState, useEffect, ChangeEvent, DragEvent } from "react";
import { FaUpload, FaTrash, FaSpinner, FaCheck } from "react-icons/fa";
import { useTranslation } from "react-i18next";
import { getAuthData } from "@/utils/auth";

type UploadResult = {
  success: true;
  jobId: string;
  filename: string;
  music: string | null;
  url: string;
  musicUrl: string | null;
};

export default function UploadVideo({
  onUploadComplete,
  maxSizeMB = 1024,
}: {
  onUploadComplete?: (data: UploadResult) => void;
  maxSizeMB?: number;
}) {
  const { t } = useTranslation();
  const [video, setVideo] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const validateFile = (file: File) => {
    if (!file.type.startsWith("video/")) {
      setError(t("upload.invalidType"));
      return false;
    }
    if (file.size > maxSizeMB * 1024 * 1024) {
      setError(t("upload.tooLarge", { max: maxSizeMB }));
      return false;
    }
    return true;
  };

  const handleUpload = async (file: File | null) => {
    if (!file || !validateFile(file) || loading) return;

    const { token, userId } = getAuthData();
    if (!token || !userId) {
      alert("Você precisa estar logado para enviar vídeos.");
      return;
    }

    setError("");
    setLoading(true);
    setSuccess(false);

    const formData = new FormData();
    formData.append("file", file); // ✅ nome correto
    formData.append("userId", userId);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("❌ Erro ao enviar vídeo:", data);
        setError(data.error || "Erro desconhecido");
      } else {
        console.log("✅ Vídeo enviado com sucesso:", data);
        setVideo(file);
        setSuccess(true);
        onUploadComplete?.(data); // envia info ao pai
      }
    } catch (err) {
      console.error("❌ Erro inesperado:", err);
      setError(t("upload.failed"));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    handleUpload(file ?? null);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    handleUpload(file ?? null);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => setDragging(false);

  const handleClear = () => {
    setVideo(null);
    setPreviewUrl(null);
    setError("");
    setSuccess(false);
  };

  useEffect(() => {
    if (!video) return;
    const url = URL.createObjectURL(video);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [video]);

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      tabIndex={0}
      role="region"
      aria-label={t("upload.dropRegion")}
      className={`p-5 border-2 rounded-xl transition-all backdrop-blur-lg text-white ${
        dragging
          ? "border-dashed border-[var(--color-accent)] bg-gray-800/80"
          : "border border-gray-600 bg-black/60"
      }`}
    >
      <label
        htmlFor="video-input"
        className="block text-sm font-medium mb-2 cursor-pointer"
      >
        <FaUpload className="inline-block mr-2" />
        {t("upload.label")}
      </label>

      <input
        id="video-input"
        type="file"
        accept="video/*"
        onChange={handleChange}
        className="w-full file:hidden"
        disabled={loading}
      />

      {error && <p className="text-red-400 text-sm mt-2">{error}</p>}

      {video ? (
        <div className="mt-4 space-y-3 text-sm text-[var(--color-accent)]">
          <p>
            🎬 <strong>{video.name}</strong> {t("upload.selected")}
          </p>

          {previewUrl && (
            <video
              src={previewUrl}
              controls
              className="w-full max-h-[500px] rounded-md border border-gray-600 object-contain shadow"
            />
          )}

          {loading ? (
            <div className="text-yellow-300 flex items-center gap-2">
              <FaSpinner className="animate-spin" /> {t("upload.uploading")}
            </div>
          ) : success ? (
            <div className="text-green-400 flex items-center gap-2">
              <FaCheck /> {t("upload.success")}
            </div>
          ) : null}

          <button
            onClick={handleClear}
            className="mt-2 px-4 py-2 flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white text-sm rounded-md transition"
            disabled={loading}
          >
            <FaTrash /> {t("upload.remove")}
          </button>
        </div>
      ) : (
        <p className="text-sm text-gray-400 mt-3">{t("upload.none")}</p>
      )}
    </div>
  );
}
