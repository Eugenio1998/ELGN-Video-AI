import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { thumbnailQueue } from "../../jobs/queue";

interface GenerateThumbnailRequest {
  jobId: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ error: "Método não permitido. Use POST." });
  }

  // 🔐 Autenticação
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];

  if (!token || !verifyToken(token)) {
    return res
      .status(401)
      .json({ error: "Não autorizado. Token ausente ou inválido." });
  }

  const { jobId } = req.body as GenerateThumbnailRequest;

  if (!jobId || typeof jobId !== "string") {
    return res.status(400).json({
      error: "Campo 'jobId' é obrigatório e deve ser uma string.",
    });
  }

  try {
    // 🎯 Enviar job para fila real
    await thumbnailQueue.add("generate-thumbnail", { jobId });

    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
    const thumbnailUrl = `${siteUrl}/thumbnails/${jobId}.jpg`;

    console.info(`🖼️ Thumbnail agendada com sucesso para job ${jobId}`);

    return res.status(200).json({
      success: true,
      jobId,
      thumbnailUrl,
      message: "Geração de thumbnail iniciada. Verifique em instantes.",
    });
  } catch (error) {
    console.error("❌ Erro ao gerar thumbnail:", error);
    return res
      .status(500)
      .json({ error: "Erro interno ao processar geração de thumbnail." });
  }
}
