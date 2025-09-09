import { isTokenExpired } from "./tokenUtils";

export async function uploadVideo(file: File) {
  const token = localStorage.getItem("token");

  if (!token || token.split(".").length !== 3 || isTokenExpired(token)) {
    console.error("❌ Token JWT ausente, malformado ou expirado.");
    throw new Error("Token JWT inválido ou expirado.");
  }

  const formData = new FormData();
  formData.append("file", file); // ⚠️ o backend espera exatamente "file"

  const response = await fetch("/api/upload", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data?.error || "Erro desconhecido no upload.");
  }

  return data;
}
