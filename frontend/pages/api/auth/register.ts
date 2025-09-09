// 📁 pages/api/auth/register.ts
import axios from "axios";
import type { NextApiRequest, NextApiResponse } from "next";
// ❌ (temporariamente desabilitado) import rateLimit from "../auth/rate-limit";

// const limiter = rateLimit({
//   interval: 60 * 1000,
//   uniqueTokenPerInterval: 500,
// });

/**
 * 🔐 Rota de registro de usuário.
 * Encaminha dados para o backend real via Axios.
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ error: "Method Not Allowed" });
  }

  try {
    // 🔍 LOG: método e IP
    const ip =
      (req.headers["x-forwarded-for"] as string) ||
      req.socket.remoteAddress ||
      "";

    console.info("📩 Requisição de registro recebida");
    console.info("🌐 IP:", ip);

    // 🔍 LOG: dados recebidos
    console.log("📥 Dados recebidos do frontend:", req.body);

    // ❌ Desabilitando temporariamente rate-limit para debug
    // if (!ip.includes("127.0.0.1") && !ip.includes("::1")) {
    //   await limiter.check(res, 5, ip);
    // }

    // 🔗 Envio para o backend
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    const { email, password, username } = req.body;

    if (!email || !password || !username) {
      return res
        .status(400)
        .json({ error: "Campos obrigatórios não enviados" });
    }

    const response = await axios.post(`${backendUrl}/api/v1/auth/register`, {
      email,
      password,
      username,
    });

    console.log("✅ Resposta do backend:", response.data);
    return res.status(200).json(response.data);
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      console.error("❌ Erro do backend:", error.response?.data);
      const detail =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.response?.data?.error;
      return res.status(400).json({
        error: detail || "Erro ao registrar usuário",
      });
    }

    console.error("❌ Erro inesperado no registro:", error);
    return res.status(500).json({ error: "Erro inesperado no servidor" });
  }
}
