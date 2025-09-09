// 📁 pages/api/apply-cuts.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { cutQueue } from "../../jobs/queue";

interface ApplyCutsRequestBody {
  jobId: string;
}

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

  // 🔐 Verifica token JWT
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];

  if (!token || !verifyToken(token)) {
    return res.status(401).json({
      success: false,
      message: "Não autorizado. Token ausente ou inválido.",
    });
  }

  const { jobId } = req.body as ApplyCutsRequestBody;

  if (!jobId || typeof jobId !== "string" || jobId.trim().length < 6) {
    return res.status(400).json({
      success: false,
      message: "O campo 'jobId' é obrigatório e deve ser válido.",
    });
  }

  try {
    // Envia para fila
    await cutQueue.add("apply-cuts", { jobId });

    console.info(`✂️ IA de cortes solicitada para o job ${jobId}`);

    return res.status(200).json({
      success: true,
      message: `Cortes enviados para processamento com IA.`,
      jobId,
    });
  } catch (err) {
    console.error("❌ Erro ao enviar cortes para fila:", err);
    return res.status(500).json({
      success: false,
      message: "Erro interno ao acionar IA de cortes.",
    });
  }
}
