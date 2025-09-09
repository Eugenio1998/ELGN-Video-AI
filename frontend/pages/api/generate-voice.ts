import type { NextApiRequest, NextApiResponse } from "next";
import OpenAI from "openai";
import { verifyToken } from "../../utils/jwt";

// 🔐 Verificação da chave OpenAI
if (!process.env.OPENAI_API_KEY) {
  throw new Error("❌ OPENAI_API_KEY não configurada no ambiente.");
}

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// 🎤 Lista de vozes válidas
const validVoices = [
  "nova",
  "alloy",
  "ash",
  "coral",
  "echo",
  "fable",
  "onyx",
  "sage",
  "shimmer",
] as const;

type VoiceType = (typeof validVoices)[number];

interface VoiceRequestBody {
  text: string;
  voice?: VoiceType;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ error: "Método não permitido. Use POST." });
  }

  // 🔐 Autenticação JWT
  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];
  if (!token || !verifyToken(token)) {
    return res
      .status(401)
      .json({ error: "Não autorizado. Token ausente ou inválido." });
  }

  const { text, voice = "nova" } = req.body as VoiceRequestBody;

  if (!text || typeof text !== "string" || !text.trim()) {
    return res.status(400).json({
      error: "O campo 'text' é obrigatório e deve conter texto válido.",
    });
  }

  if (!validVoices.includes(voice)) {
    return res.status(400).json({
      error: `Voz '${voice}' inválida. Escolha uma das seguintes: ${validVoices.join(
        ", "
      )}`,
    });
  }

  try {
    const response = await openai.audio.speech.create({
      input: text,
      model: "tts-1-hd",
      voice,
      response_format: "mp3",
    });

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("Content-Disposition", "attachment; filename=voice.mp3");
    return res.status(200).send(buffer);
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : "Erro desconhecido";
    console.error("❌ Erro ao gerar voz IA:", errorMessage);
    return res.status(500).json({
      error: "Erro ao gerar narração com IA",
      details: errorMessage,
    });
  }
}
