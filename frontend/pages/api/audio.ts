import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";
import { audioQueue } from "../../jobs/queue";

interface AudioRequest {
  prompt: string;
  type?: "music" | "voice";
  genre?: string;
  voiceId?: string;
  language?: string;
  emotion?: string;
  duration?: number;
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
  if (!token || !verifyToken(token)) {
    return res.status(401).json({ error: "Token ausente ou inválido." });
  }

  const {
    prompt,
    type = "music",
    genre = "ambient",
    voiceId = "default",
    language = "en",
    emotion = "neutral",
    duration = 10,
  }: AudioRequest = req.body;

  if (!prompt || typeof prompt !== "string") {
    return res
      .status(400)
      .json({ error: "O campo 'prompt' é obrigatório e deve ser texto." });
  }

  if (!["music", "voice"].includes(type)) {
    return res
      .status(400)
      .json({ error: "O campo 'type' deve ser 'music' ou 'voice'." });
  }

  try {
    const job = await audioQueue.add("generate-audio", {
      prompt,
      type,
      genre,
      voiceId,
      language,
      emotion,
      duration,
    });

    console.info(`🎧 Áudio (${type}) adicionado à fila com ID: ${job.id}`);

    return res.status(200).json({
      success: true,
      message: "Geração de áudio em andamento. Verifique o status em breve.",
      jobId: job.id,
    });
  } catch (err) {
    console.error("Erro ao adicionar áudio à fila:", err);
    return res.status(500).json({ error: "Erro interno ao processar áudio." });
  }
}
