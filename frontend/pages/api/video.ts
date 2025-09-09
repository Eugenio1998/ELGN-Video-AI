// 📁 pages/api/video.ts

import type { NextApiRequest, NextApiResponse } from "next";
import { verifyToken } from "../../utils/verifyToken";

type VideoResponse = {
  success: true;
  video_url: string;
  details: {
    prompt: string;
    type: string;
    imageUrl: string;
    duration: number;
    resolution: string;
  };
};

type ErrorResponse = {
  error: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<VideoResponse | ErrorResponse>
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ error: "Método não permitido" });
  }

  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Não autorizado" });
  }

  const token = authHeader.split(" ")[1];
  const user = verifyToken(token);
  if (!user) {
    return res.status(401).json({ error: "Token inválido ou expirado" });
  }

  const {
    prompt,
    type = "text-to-video",
    imageUrl = "",
    duration = 4,
    resolution = "720p",
  } = req.body;

  const allowedTypes = [
    "text-to-video",
    "image-to-video",
    "motion-expand",
    "inpainting",
  ];

  if (!prompt || typeof prompt !== "string") {
    return res.status(400).json({ error: "O campo 'prompt' é obrigatório." });
  }

  if (!allowedTypes.includes(type)) {
    return res.status(400).json({ error: "Tipo de geração inválido." });
  }

  try {
    const runwayResponse = await fetch("https://api.runwayml.com/v1/gen2", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.RUNWAY_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt,
        type,
        image_url: imageUrl,
        duration,
        resolution,
      }),
    });

    const data = await runwayResponse.json();

    if (!runwayResponse.ok || !data.video_url) {
      console.error("❌ Runway API error:", data);
      return res
        .status(502)
        .json({ error: "Erro ao gerar vídeo com Runway AI." });
    }

    console.log("✅ Vídeo gerado com sucesso via Runway:", data.video_url);

    return res.status(200).json({
      success: true,
      video_url: data.video_url,
      details: { prompt, type, imageUrl, duration, resolution },
    });
  } catch (error) {
    console.error("❌ Erro interno ao gerar vídeo:", error);
    return res.status(500).json({ error: "Erro interno na geração de vídeo." });
  }
}
