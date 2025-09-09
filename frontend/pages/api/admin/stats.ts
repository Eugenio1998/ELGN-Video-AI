// 📁 pages/api/admin/stats.ts
import type { NextApiRequest, NextApiResponse } from "next";
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET || "elgn-fallback-secret";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "GET") {
    return res
      .status(405)
      .json({ status: "error", message: "Método não permitido" });
  }

  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ status: "error", message: "Token ausente" });
  }

  const token = authHeader.split(" ")[1];

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as { role?: string };

    if (decoded.role !== "admin") {
      return res
        .status(403)
        .json({ status: "error", message: "Acesso negado" });
    }

    const stats = {
      totalUsers: 347,
      totalVideosGerados: 1294,
      totalJobsAtivos: 42,
      planoPremium: 87,
      planoPro: 122,
      planoBasic: 138,
    };

    return res.status(200).json({
      status: "success",
      stats,
      timestamp: new Date().toISOString(),
    });
  } catch {
    return res.status(401).json({ status: "error", message: "Token inválido" });
  }
}
