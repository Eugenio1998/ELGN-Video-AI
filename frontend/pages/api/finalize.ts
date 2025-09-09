import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { finalizeQueue } from "../../jobs/queue";

interface FinalizeRequest {
  jobId: string;
  includeWatermark?: boolean;
  format?: string;
}

interface FinalizeResponse {
  success: boolean;
  message: string;
  jobId?: string;
  outputUrl?: string;
  error?: string;
}

const supportedFormats = ["mp4", "mov", "webm", "mkv"];

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<FinalizeResponse>
) {
  if (req.method !== "POST") {
    return res.status(405).json({
      success: false,
      message: "Método não permitido. Use POST.",
    });
  }

  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];
  if (!token || !verifyToken(token)) {
    return res.status(401).json({
      success: false,
      message: "Não autorizado. Token ausente ou inválido.",
    });
  }

  const {
    jobId,
    includeWatermark = true,
    format = "mp4",
  } = req.body as FinalizeRequest;

  if (!jobId || typeof jobId !== "string") {
    return res.status(400).json({
      success: false,
      message: "O campo 'jobId' é obrigatório e deve ser uma string.",
    });
  }

  if (!supportedFormats.includes(format)) {
    return res.status(400).json({
      success: false,
      message: `Formato '${format}' não suportado. Use um dos seguintes: ${supportedFormats.join(
        ", "
      )}`,
    });
  }

  try {
    await finalizeQueue.add("finalize-video", {
      jobId,
      includeWatermark,
      format,
    });

    const outputUrl = `/output/final-${jobId}.${format}`;

    console.info(
      `🎬 Finalização agendada: job=${jobId}, watermark=${includeWatermark}, formato=${format}`
    );

    return res.status(200).json({
      success: true,
      message: `Finalização agendada para o job ${jobId}`,
      jobId,
      outputUrl,
    });
  } catch (error) {
    console.error("❌ Erro ao enfileirar finalização:", error);
    return res.status(500).json({
      success: false,
      message: "Erro interno na finalização do vídeo.",
    });
  }
}
