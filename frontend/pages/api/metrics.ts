// 📁 pages/api/metrics.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Método não permitido" });
  }

  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];

  if (!token) {
    console.warn("📛 Token de autenticação ausente na chamada de /metrics");
    return res.status(401).json({ error: "Token de autenticação ausente." });
  }

  try {
    verifyToken(token);
  } catch (err) {
    console.warn("🔐 Token inválido ou expirado:", err);
    return res.status(403).json({ error: "Token inválido ou expirado." });
  }

  // 🔢 Métricas básicas
  const uptime = process.uptime(); // tempo desde que o servidor iniciou
  const memoryUsage = process.memoryUsage(); // uso de memória atual

  const metrics = [
    `# HELP app_uptime_seconds Tempo de atividade do servidor.`,
    `# TYPE app_uptime_seconds gauge`,
    `app_uptime_seconds ${uptime.toFixed(2)}`,

    `# HELP app_memory_usage_bytes Uso de memória RSS em bytes.`,
    `# TYPE app_memory_usage_bytes gauge`,
    `app_memory_usage_bytes ${memoryUsage.rss}`,

    // Futuro: adicionar CPU usage, event loop lag, filas, jobs, etc.
  ];

  res.setHeader("Content-Type", "text/plain");
  console.info("📈 Métricas acessadas com sucesso.");
  return res.status(200).send(metrics.join("\n"));
}
