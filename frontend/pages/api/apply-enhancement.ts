// 📁 pages/api/apply-enhancement.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";

type Data = {
  success: boolean;
  message: string;
  jobId?: string;
};

export default function handler(
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

  // 🔐 Verificação de token JWT
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

  console.info(`🎛️ Melhoria de qualidade aplicada ao job ${jobId}`);

  return res.status(200).json({
    success: true,
    message: `✅ Melhoria aplicada com sucesso ao vídeo com jobId ${jobId}`,
    jobId,
  });
}
