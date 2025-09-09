// 📁 pages/api/apply-voice.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { voiceQueue } from "../../jobs/queue";

interface ApplyVoiceRequest {
  jobId: string;
  voiceType: string;
}

type SuccessResponse = {
  success: true;
  message: string;
  jobId: string;
  voiceType: string;
};

type ErrorResponse = {
  success?: false;
  error: string;
};

const allowedVoices = [
  "default",
  "female",
  "male",
  "robot",
  "narrator",
  "child",
  "emotion",
  "ai",
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
      .json({ error: "Não autorizado. Token ausente ou inválido." });
  }

  const { jobId, voiceType } = req.body as ApplyVoiceRequest;

  if (
    !jobId ||
    typeof jobId !== "string" ||
    !voiceType ||
    typeof voiceType !== "string"
  ) {
    return res.status(400).json({
      error:
        "Campos 'jobId' e 'voiceType' são obrigatórios e devem ser strings.",
    });
  }

  if (!allowedVoices.includes(voiceType)) {
    return res.status(400).json({
      error: `Voz inválida. Use uma das seguintes: ${allowedVoices.join(", ")}`,
    });
  }

  try {
    await voiceQueue.add("apply-voice", { jobId, voiceType });

    console.info(`🗣️ Voz '${voiceType}' aplicada ao job '${jobId}'`);

    return res.status(200).json({
      success: true,
      message: `Voz '${voiceType}' aplicada com sucesso ao job '${jobId}'`,
      jobId,
      voiceType,
    });
  } catch (err) {
    console.error("❌ Erro ao aplicar voz:", err);
    return res.status(500).json({ error: "Erro interno ao aplicar voz." });
  }
}
