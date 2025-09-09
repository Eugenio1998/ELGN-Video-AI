// 📁 utils/formatDate.ts

/**
 * Formata uma data de acordo com o idioma selecionado.
 * Exemplo:
 * - pt-BR: 01/06/2025 14:33
 * - en-US: Jun 1, 2025, 2:33 PM
 */
export function formatDate(
  input: string | Date,
  locale: string = navigator.language || "pt-BR"
): string {
  const date = new Date(input);
  if (isNaN(date.getTime())) {
    console.warn("❌ formatDate: data inválida fornecida:", input);
    return "Data inválida";
  }

  const formatter = new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });

  return formatter.format(date);
}
