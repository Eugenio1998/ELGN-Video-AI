// 📁 pages/api/apply-enhancement.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { enhancementQueue } from "../../jobs/queue";

type Data = {
  success: boolean;
  message: string;
  jobId?: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<Data>
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({
      success: false,
      message: `Método ${req.method} não permitido.`,
    });
  }

  // 🔐 Verificação JWT
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];

  if (!token || !verifyToken(token)) {
    return res.status(401).json({
      success: false,
      message: "Não autorizado. Token ausente ou inválido.",
    });
  }

  const { jobId } = req.body as { jobId?: string };

  if (!jobId || typeof jobId !== "string" || jobId.trim().length < 6) {
    return res.status(400).json({
      success: false,
      message: "O campo 'jobId' é obrigatório e deve ser válido.",
    });
  }

  try {
    // ✅ Chamada real da fila BullMQ para aplicar melhoria
    await enhancementQueue.add("enhance", { jobId });

    console.info(`🎛️ Job ${jobId} enviado para fila de melhoria de qualidade.`);

    return res.status(200).json({
      success: true,
      message: `Melhoria enviada para processamento no job ${jobId}`,
      jobId,
    });
  } catch (error) {
    console.error("❌ Erro ao adicionar tarefa de melhoria:", error);
    return res.status(500).json({
      success: false,
      message: "Erro interno ao processar melhoria de qualidade.",
    });
  }
}
