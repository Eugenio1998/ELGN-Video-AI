import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { exportQueue } from "../../jobs/queue";

interface FinalizeExportRequest {
  jobId: string;
}

interface FinalizeExportResponse {
  success: boolean;
  message: string;
  jobId?: string;
  downloadUrl?: string;
  error?: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<FinalizeExportResponse>
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

  const { jobId } = req.body as FinalizeExportRequest;

  if (!jobId || typeof jobId !== "string") {
    return res.status(400).json({
      success: false,
      message: "Campo 'jobId' é obrigatório e deve ser uma string.",
    });
  }

  try {
    await exportQueue.add("finalize-export", { jobId });

    const downloadUrl = `/output/${jobId}-final.mp4`;

    console.info(`🎞️ Exportação final iniciada para job ${jobId}`);

    return res.status(200).json({
      success: true,
      message: "Vídeo final exportado com sucesso.",
      jobId,
      downloadUrl,
    });
  } catch (error) {
    console.error("❌ Erro interno na exportação:", error);
    return res.status(500).json({
      success: false,
      message: "Erro interno na exportação do vídeo.",
    });
  }
}
