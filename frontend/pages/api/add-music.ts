// 📁 pages/api/add-music.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { addMusicQueue } from "../../jobs/queue";
import { verifyToken, DecodedToken } from "../../utils/jwt";

interface AddMusicBody {
  jobId: string;
  musicUrl: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Método não permitido. Use POST." });
  }

  // 🔐 Verifica autenticação via token JWT
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];

  const decoded: DecodedToken | null = token ? verifyToken(token) : null;

  if (!decoded || !decoded.id) {
    return res
      .status(401)
      .json({ error: "Não autorizado. Token inválido ou ausente." });
  }

  // ✅ Validação básica do body
  const { jobId, musicUrl } = req.body as AddMusicBody;

  if (!jobId || !musicUrl) {
    return res.status(400).json({
      error: "Campos obrigatórios: 'jobId' e 'musicUrl'.",
    });
  }

  const isValidUrl = /^https?:\/\/.+/.test(musicUrl);
  if (!isValidUrl) {
    return res.status(400).json({ error: "URL da música inválida." });
  }

  try {
    // 📥 Envia a tarefa para a fila BullMQ com ID do usuário
    await addMusicQueue.add("process", {
      jobId,
      musicUrl,
      userId: decoded.id,
    });

    console.info(
      `📨 Tarefa adicionada à fila para o job ${jobId} com música ${musicUrl} (Usuário: ${decoded.id})`
    );

    return res.status(200).json({
      success: true,
      message: "Música enviada para processamento.",
      jobId,
    });
  } catch (err) {
    console.error("❌ Erro ao adicionar à fila:", err);
    return res
      .status(500)
      .json({ error: "Erro interno ao enviar tarefa para fila." });
  }
}
