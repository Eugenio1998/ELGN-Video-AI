// 📁 utils/downloadFile.ts

/**
 * Dispara o download de um arquivo no navegador.
 * Suporta URLs públicas, Blobs e strings base64.
 */
export function downloadFile(source: string | Blob, filename: string): void {
  let blobUrl: string;

  if (source instanceof Blob) {
    blobUrl = URL.createObjectURL(source);
  } else if (typeof source === "string" && source.startsWith("data:")) {
    blobUrl = source;
  } else if (typeof source === "string") {
    blobUrl = source;
  } else {
    console.error("❌ downloadFile: tipo de fonte não suportado");
    return;
  }

  const link = document.createElement("a");
  link.href = blobUrl;
  link.download = filename || "download";
  link.rel = "noopener noreferrer";
  link.target = "_blank";
  link.style.display = "none";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  if (source instanceof Blob) {
    URL.revokeObjectURL(blobUrl);
  }
}
