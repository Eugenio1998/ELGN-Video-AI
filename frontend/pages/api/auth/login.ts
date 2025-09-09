// 📁 pages/api/auth/login.ts
import axios from "axios";
import type { NextApiRequest, NextApiResponse } from "next";
import rateLimit from "../auth/rate-limit";

const limiter = rateLimit({ interval: 60 * 1000, uniqueTokenPerInterval: 500 });

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).end("Method Not Allowed");
  }

  // 🚫 Validação básica dos campos
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: "Email e senha são obrigatórios" });
  }

  try {
    // 🛡️ Rate limit por IP
    const ip =
      (req.headers["x-forwarded-for"] as string) ||
      req.socket.remoteAddress ||
      "";
    await limiter.check(res, 5, ip);

    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    const response = await axios.post(
      `${backendUrl}/api/v1/auth/login`,
      { email, password },
      {
        headers: {
          "Content-Type": "application/json",
        },
        timeout: 5000, // ⏱️ timeout de 5s
      }
    );

    return res.status(200).json(response.data);
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const detail =
        error.response?.data?.detail || error.response?.data?.message;
      return res.status(400).json({ error: detail || "Erro ao fazer login" });
    }

    console.error("❌ Erro inesperado no login:", error);
    return res.status(500).json({ error: "Erro inesperado no servidor" });
  }
}
