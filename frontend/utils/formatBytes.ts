// 📁 utils/formatBytes.ts
/**
 * Converte bytes em string legível com suporte a internacionalização.
 * Exemplo: 1.23 MB (en-US) ou 1,23 MB (pt-BR)
 */
export function formatBytes(
  bytes: number,
  decimals = 2,
  locale: string = navigator.language || "en-US"
): string {
  if (bytes === 0 || isNaN(bytes) || bytes < 0) return "0 Bytes";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const value = parseFloat((bytes / Math.pow(k, i)).toFixed(dm));

  return `${new Intl.NumberFormat(locale, {
    minimumFractionDigits: dm,
    maximumFractionDigits: dm,
  }).format(value)} ${sizes[i]}`;
}
