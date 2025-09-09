// 📁 pages/api/compress.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { compressionQueue } from "../../jobs/queue";

interface CompressRequest {
  jobId: string;
  targetSizeMb: number;
}

interface CompressResponse {
  success: boolean;
  message: string;
  jobId?: string;
  targetSizeMb?: number;
  error?: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<CompressResponse>
) {
  if (req.method !== "POST") {
    return res
      .status(405)
      .json({ success: false, message: "Método não permitido. Use POST." });
  }

  // 🔐 Autenticação via JWT
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];

  if (!token || !verifyToken(token)) {
    return res.status(401).json({
      success: false,
      message: "Não autorizado. Token ausente ou inválido.",
    });
  }

  const { jobId, targetSizeMb } = req.body as CompressRequest;

  if (!jobId || typeof targetSizeMb !== "number" || targetSizeMb < 1) {
    return res.status(400).json({
      success: false,
      message:
        "Campos 'jobId' (string) e 'targetSizeMb' (número positivo) são obrigatórios.",
    });
  }

  try {
    await compressionQueue.add("compress-video", { jobId, targetSizeMb });

    console.info(
      `🗜️ Compressão agendada para job ${jobId}, alvo: ${targetSizeMb}MB`
    );

    return res.status(200).json({
      success: true,
      message: `Compressão em andamento para job ${jobId} (≈${targetSizeMb}MB)`,
      jobId,
      targetSizeMb,
    });
  } catch (err) {
    console.error("Erro ao enfileirar compressão:", err);
    return res.status(500).json({
      success: false,
      message: "Erro interno ao iniciar compressão.",
    });
  }
}
