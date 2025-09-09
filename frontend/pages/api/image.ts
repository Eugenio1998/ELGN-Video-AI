// 📁 pages/api/image.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/jwt";

// 🎨 Opções válidas
const validSizes = ["1024x1024", "1792x1024", "1024x1792"] as const;
const validStyles = ["vivid", "natural"] as const;

type RequestData = {
  prompt: string;
  size?: (typeof validSizes)[number];
  style?: (typeof validStyles)[number];
};

type ResponseData = {
  imageUrl?: string;
  prompt?: string;
  size?: string;
  style?: string;
  error?: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Método não permitido" });
  }

  const authHeader = req.headers.authorization;
  const token = authHeader?.split(" ")[1];
  if (!token || !verifyToken(token)) {
    return res.status(401).json({ error: "Não autorizado. Token inválido." });
  }

  const {
    prompt,
    size = "1024x1024",
    style = "vivid",
  } = req.body as RequestData;

  if (!prompt?.trim()) {
    return res.status(400).json({ error: "Prompt é obrigatório." });
  }

  if (!validSizes.includes(size)) {
    return res.status(400).json({ error: `Tamanho '${size}' inválido.` });
  }

  if (!validStyles.includes(style)) {
    return res.status(400).json({ error: `Estilo '${style}' inválido.` });
  }

  try {
    const response = await fetch(
      "https://api.openai.com/v1/images/generations",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: "dall-e-3",
          prompt,
          size,
          style,
          n: 1,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error("❌ Erro OpenAI:", data.error);
      return res
        .status(500)
        .json({ error: data.error?.message || "Erro ao gerar imagem." });
    }

    const imageUrl = data.data?.[0]?.url;
    if (!imageUrl) {
      console.error("❌ Nenhuma URL de imagem retornada.");
      return res
        .status(500)
        .json({ error: "A imagem não foi retornada pela IA." });
    }

    console.info("🖼️ Imagem gerada com sucesso:", imageUrl);

    return res.status(200).json({
      imageUrl,
      prompt,
      size,
      style,
    });
  } catch (err) {
    console.error("❌ Erro inesperado:", err);
    return res.status(500).json({ error: "Erro interno ao gerar imagem." });
  }
}
