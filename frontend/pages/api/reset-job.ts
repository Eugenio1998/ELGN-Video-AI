// 📁 pages/api/reset-job.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/verifyToken";

type JobResetResponse = {
  success: boolean;
  jobId: string;
  message: string;
};

type ErrorResponse = {
  error: string;
  details?: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<JobResetResponse | ErrorResponse>
) {
  // 🚫 Permitir apenas método POST
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ error: "Método não permitido. Use POST." });
  }

  // 🔐 Autenticação via token JWT
  const token = req.headers.authorization?.split(" ")[1];
  if (!token || !verifyToken(token)) {
    return res.status(401).json({ error: "Não autorizado. Token inválido." });
  }

  // 📥 Dados esperados do body
  const { jobId } = req.body as { jobId?: string };

  if (!jobId || typeof jobId !== "string") {
    return res.status(400).json({
      error: "Campo 'jobId' é obrigatório e deve ser uma string.",
    });
  }

  try {
    // 🔄 Simula reset do job (poderia integrar com fila de jobs real)
    console.info(`♻️ Resetando job ID: ${jobId} para novo processamento`);

    return res.status(200).json({
      success: true,
      jobId,
      message: "Job resetado com sucesso para novo teste ou edição.",
    });
  } catch (error: unknown) {
    if (error instanceof Error) {
      console.error("❌ Erro ao resetar job:", error.message);
      return res.status(500).json({
        error: "Erro ao resetar job",
        details: error.message,
      });
    }
    console.error("❌ Erro desconhecido ao resetar job:", error);
    return res.status(500).json({ error: "Erro interno ao resetar job" });
  }
}
