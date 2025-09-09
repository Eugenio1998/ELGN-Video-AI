// 📁 pages/api/apply-style.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { styleQueue } from "../../jobs/queue";

interface ApplyStyleRequest {
  jobId: string;
  style: string;
}

type SuccessResponse = {
  success: true;
  message: string;
  jobId: string;
  style: string;
};

type ErrorResponse = {
  success?: false;
  error: string;
};

const allowedStyles = [
  "cyberpunk",
  "cartoon",
  "anime",
  "vintage",
  "cinematic",
  "pencil",
  "oil",
  "watercolor",
  "glitch",
];

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<SuccessResponse | ErrorResponse>
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Método não permitido. Use POST." });
  }

  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];

  if (!token || !verifyToken(token)) {
    return res
      .status(401)
      .json({ error: "Não autorizado. Token inválido ou ausente." });
  }

  const { jobId, style } = req.body as ApplyStyleRequest;

  if (
    !jobId ||
    typeof jobId !== "string" ||
    !style ||
    typeof style !== "string"
  ) {
    return res.status(400).json({
      error: "Campos 'jobId' e 'style' são obrigatórios e devem ser strings.",
    });
  }

  if (!allowedStyles.includes(style)) {
    return res.status(400).json({
      error: `Estilo inválido. Use um dos seguintes: ${allowedStyles.join(
        ", "
      )}`,
    });
  }

  try {
    await styleQueue.add("apply-style", { jobId, style });

    console.info(`🎨 Estilo '${style}' enviado para job '${jobId}'`);

    return res.status(200).json({
      success: true,
      message: `Estilo '${style}' aplicado com sucesso ao job '${jobId}'`,
      jobId,
      style,
    });
  } catch (error) {
    console.error("❌ Erro ao aplicar estilo:", error);
    return res
      .status(500)
      .json({ error: "Erro interno ao aplicar estilo visual." });
  }
}
