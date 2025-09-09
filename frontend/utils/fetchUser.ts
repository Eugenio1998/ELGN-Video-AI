// 📁 utils/fetchUser.ts
import axios from "axios";

/**
 * Busca os dados do usuário logado com base no token JWT.
 * Atualiza localStorage e pode ser expandido para atualizar contexto global.
 */
export const fetchUser = async (token: string) => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  if (!token || token.split(".").length !== 3) {
    console.warn("❌ Token JWT ausente ou malformado.");
    throw new Error("Token de autenticação inválido.");
  }

  try {
    const response = await axios.get(`${API_URL}/api/v1/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    const userData = response.data;

    if (!userData) {
      throw new Error("Resposta vazia ao buscar usuário.");
    }

    // 🧠 Armazena os dados localmente
    localStorage.setItem("user", JSON.stringify(userData));

    // 🔁 Atualização do contexto global pode ser feita aqui futuramente

    return userData;
  } catch (error: unknown) {
    const message =
      axios.isAxiosError(error) && error.response?.data?.detail
        ? error.response.data.detail
        : "Erro desconhecido ao buscar usuário.";

    console.error("❌ fetchUser:", message);
    throw new Error(message);
  }
};
