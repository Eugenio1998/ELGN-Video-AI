// 📁 pages/api/auth/logout.ts
import type { NextApiRequest, NextApiResponse } from "next";
import rateLimit from "../auth/rate-limit"; // ⚠️ Reutiliza middleware existente

// ⏳ Limita 5 requisições por minuto por IP
const limiter = rateLimit({ interval: 60 * 1000, uniqueTokenPerInterval: 500 });

/**
 * Rota de logout: pode ser expandida para revogar tokens no backend.
 * Atualmente limpa sessão apenas no client-side (ex: localStorage/cookies).
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).end("Method Not Allowed");
  }

  try {
    // 🛡️ Proteção contra abuso por IP
    const ip =
      (req.headers["x-forwarded-for"] as string) ||
      req.socket.remoteAddress ||
      "";
    await limiter.check(res, 5, ip);

    // 🛑 (Opcional) Revogação de token no backend
    // const token = req.headers.authorization?.replace("Bearer ", "");
    // if (token) {
    //   await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/logout`, {}, {
    //     headers: { Authorization: `Bearer ${token}` }
    //   });
    // }

    console.info("🔓 Logout realizado com sucesso.");
    return res.status(200).json({ message: "Sessão encerrada com sucesso." });
  } catch {
    console.warn("⚠️ Excesso de tentativas de logout.");
    return res
      .status(429)
      .json({ error: "Muitas requisições. Tente novamente em instantes." });
  }
}
