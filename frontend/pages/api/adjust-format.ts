// 📁 pages/api/adjust-format.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { formatQueue } from "../../jobs/queue";

type TargetFormat =
  | "square"
  | "vertical"
  | "horizontal"
  | "landscape"
  | "portrait";

interface AdjustFormatRequestBody {
  jobId: string;
  targetFormat: TargetFormat;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Método não permitido. Use POST." });
  }

  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];

  const decoded = token ? verifyToken(token) : null;
  if (!decoded) {
    return res
      .status(401)
      .json({ error: "Não autorizado. Token ausente ou inválido." });
  }

  const { jobId, targetFormat } = req.body as AdjustFormatRequestBody;

  if (!jobId || typeof jobId !== "string" || jobId.length < 6) {
    return res.status(400).json({
      error: "ID do job inválido ou ausente.",
    });
  }

  const acceptedFormats: TargetFormat[] = [
    "square",
    "vertical",
    "horizontal",
    "landscape",
    "portrait",
  ];
  if (!acceptedFormats.includes(targetFormat)) {
    return res.status(400).json({ error: "Formato inválido." });
  }

  try {
    await formatQueue.add("adjust-format", { jobId, targetFormat });

    console.info(
      `📐 Job ${jobId} enviado para ajuste de formato: ${targetFormat}`
    );

    return res.status(200).json({
      success: true,
      message: `Formato '${targetFormat}' enviado para processamento no job ${jobId}`,
    });
  } catch (error: unknown) {
    console.error("❌ Erro ao ajustar formato:", error);
    return res.status(500).json({ error: "Erro interno ao ajustar formato." });
  }
}
