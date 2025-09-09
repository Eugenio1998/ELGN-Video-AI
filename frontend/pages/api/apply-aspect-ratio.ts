// 📁 pages/api/apply-aspect-ratio.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { aspectRatioQueue } from "../../jobs/queue";

type AspectRatioType = "1:1" | "4:3" | "16:9" | "21:9" | "9:16";

interface ApplyAspectRatioRequest {
  jobId: string;
  aspectRatio: AspectRatioType;
}

const allowedRatios: AspectRatioType[] = ["1:1", "4:3", "16:9", "21:9", "9:16"];

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Método não permitido. Use POST." });
  }

  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];

  const decoded = token && verifyToken(token);
  if (!decoded) {
    return res
      .status(401)
      .json({ error: "Não autorizado. Token ausente ou inválido." });
  }

  const { jobId, aspectRatio } = req.body as ApplyAspectRatioRequest;

  if (!jobId || typeof jobId !== "string" || jobId.length < 6) {
    return res
      .status(400)
      .json({ error: "Campo 'jobId' inválido ou ausente." });
  }

  if (!allowedRatios.includes(aspectRatio)) {
    return res.status(400).json({
      error: "Proporção inválida. Use: 1:1, 4:3, 16:9, 21:9, 9:16",
    });
  }

  try {
    await aspectRatioQueue.add("apply-aspect", { jobId, aspectRatio });

    console.info(`📐 Proporção ${aspectRatio} enviada para job ${jobId}`);

    return res.status(200).json({
      success: true,
      message: `Proporção '${aspectRatio}' aplicada ao job ${jobId}`,
    });
  } catch (error: unknown) {
    console.error("❌ Erro ao aplicar proporção:", error);
    return res
      .status(500)
      .json({ error: "Erro interno ao aplicar proporção." });
  }
}
