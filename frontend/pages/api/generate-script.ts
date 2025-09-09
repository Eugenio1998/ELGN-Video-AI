import type { NextApiRequest, NextApiResponse } from "next";
import OpenAI from "openai";

// 🌐 Idiomas suportados
const languages: Record<string, string> = {
  pt: "em português",
  en: "in English",
  es: "en español",
  fr: "en français",
  de: "auf Deutsch",
  it: "in italiano",
  ja: "日本語で",
  zh: "中文",
  ru: "на русском",
};

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY!,
});

interface SEORequest {
  topic: string;
  language?: string;
  token: string;
  currentCredits: number;
}

interface SEOResponse {
  title?: string;
  tags?: string;
  description?: string;
  language?: string;
  creditsRemaining?: number;
  error?: string;
  details?: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<SEOResponse>
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ error: "Método não permitido. Use POST." });
  }

  const {
    topic,
    language = "pt",
    token,
    currentCredits,
  } = req.body as SEORequest;

  if (!token || typeof token !== "string" || currentCredits === undefined) {
    return res
      .status(400)
      .json({ error: "Dados do usuário incompletos ou inválidos." });
  }

  if (currentCredits <= 0) {
    return res.status(403).json({
      error: "Você atingiu seu limite de uso de SEO com IA.",
    });
  }

  if (!topic || typeof topic !== "string") {
    return res.status(400).json({ error: "O campo 'topic' é obrigatório." });
  }

  const langText = languages[language] || "em português";

  try {
    const [titleRes, tagsRes, descRes] = await Promise.all([
      openai.chat.completions.create({
        model: "gpt-4",
        temperature: 0.7,
        messages: [
          {
            role: "system",
            content:
              "Você é especialista em criar títulos curtos, impactantes e otimizados para vídeos.",
          },
          {
            role: "user",
            content: `Crie um título envolvente para um vídeo com o tema: ${topic}. Gere o título ${langText}.`,
          },
        ],
      }),
      openai.chat.completions.create({
        model: "gpt-4",
        temperature: 0.7,
        messages: [
          {
            role: "system",
            content:
              "Você gera hashtags virais e otimizadas para vídeos de redes sociais.",
          },
          {
            role: "user",
            content: `Liste de 5 a 10 hashtags populares para um vídeo com o tema: ${topic}. Apenas as hashtags separadas por vírgula, ${langText}.`,
          },
        ],
      }),
      openai.chat.completions.create({
        model: "gpt-4",
        temperature: 0.7,
        messages: [
          {
            role: "system",
            content:
              "Você cria descrições otimizadas, interessantes e com chamadas para ação.",
          },
          {
            role: "user",
            content: `Crie uma descrição envolvente para um vídeo com o tema: ${topic}. Gere a descrição ${langText}.`,
          },
        ],
      }),
    ]);

    const title = titleRes.choices[0]?.message?.content?.trim() || "";
    const tags = tagsRes.choices[0]?.message?.content?.trim() || "";
    const description = descRes.choices[0]?.message?.content?.trim() || "";

    // 🔄 Atualiza os créditos do usuário
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/seo-credits`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ decrement: 1 }),
    });

    console.info(`📊 SEO gerado com sucesso para: ${topic}`);

    return res.status(200).json({
      title,
      tags,
      description,
      language,
      creditsRemaining: currentCredits - 1,
    });
  } catch (error: unknown) {
    const message =
      error instanceof Error ? error.message : "Erro desconhecido";

    console.error("❌ Erro ao gerar SEO:", message);

    return res.status(500).json({
      error: "Erro ao gerar dados de SEO com IA",
      details: message,
    });
  }
}
