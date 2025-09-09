// 📁 hooks/useCopyToClipboard.ts
export function useCopyToClipboard() {
  return (text: string) => {
    navigator.clipboard.writeText(text).catch((err) => {
      console.error("Erro ao copiar para a área de transferência:", err);
    });
  };
}
