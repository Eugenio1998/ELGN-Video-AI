// 📁 pages/api/apply-resolution.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { resolutionQueue } from "../../jobs/queue";

interface ApplyResolutionRequest {
  jobId: string;
  resolution: string;
}

type SuccessResponse = {
  success: true;
  message: string;
  jobId: string;
  resolution: string;
};

type ErrorResponse = {
  success?: false;
  error: string;
};

const allowedResolutions = ["480p", "720p", "1080p", "1440p", "4k"];

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

  const { jobId, resolution } = req.body as ApplyResolutionRequest;

  if (
    !jobId ||
    !resolution ||
    typeof jobId !== "string" ||
    typeof resolution !== "string"
  ) {
    return res.status(400).json({
      error:
        "Campos 'jobId' e 'resolution' são obrigatórios e devem ser strings.",
    });
  }

  if (!allowedResolutions.includes(resolution)) {
    return res.status(400).json({
      error: `Resolução inválida. Use uma das seguintes: ${allowedResolutions.join(
        ", "
      )}`,
    });
  }

  try {
    await resolutionQueue.add("apply-resolution", { jobId, resolution });

    console.info(`📐 Resolução '${resolution}' enviada para job '${jobId}'`);

    return res.status(200).json({
      success: true,
      message: `Resolução '${resolution}' aplicada com sucesso ao job '${jobId}'`,
      jobId,
      resolution,
    });
  } catch (err) {
    console.error("❌ Erro ao aplicar resolução:", err);
    return res
      .status(500)
      .json({ error: "Erro interno ao aplicar resolução." });
  }
}
