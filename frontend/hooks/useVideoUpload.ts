// 📁 hooks/useVideoUpload.ts
import { useState, useCallback, useEffect } from "react";

export function useVideoUpload() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // 🧼 Limpa URL anterior da memória ao trocar o vídeo
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  // 📥 Define novo vídeo e gera URL de visualização
  const upload = useCallback((file: File) => {
    setVideoFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  }, []);

  // ❌ Limpa vídeo e preview
  const clear = useCallback(() => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setVideoFile(null);
    setPreviewUrl(null);
  }, [previewUrl]);

  return {
    videoFile,
    previewUrl,
    upload,
    clear,
  };
}
