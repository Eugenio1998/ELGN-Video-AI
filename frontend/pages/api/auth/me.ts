// 📁 pages/api/auth/me.ts
import axios from "axios";
import type { NextApiRequest, NextApiResponse } from "next";

/**
 * 🔐 Rota protegida para obter os dados do usuário autenticado.
 * Repassa o token JWT recebido no header Authorization para o backend.
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "GET") {
    res.setHeader("Allow", ["GET"]);
    return res.status(405).json({ error: "Método não permitido" });
  }

  const token = req.headers.authorization?.split(" ")[1];
  if (!token) {
    return res.status(401).json({ error: "Token não fornecido" });
  }

  try {
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    const response = await axios.get(`${backendUrl}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.data) {
      return res.status(404).json({ error: "Usuário não encontrado" });
    }

    return res.status(200).json(response.data);
  } catch (error: unknown) {
    const message =
      axios.isAxiosError(error) && error.response?.data?.detail
        ? error.response.data.detail
        : "Sessão inválida ou expirada";

    console.warn("❌ Erro em /auth/me:", message);
    return res.status(401).json({ error: message });
  }
}
