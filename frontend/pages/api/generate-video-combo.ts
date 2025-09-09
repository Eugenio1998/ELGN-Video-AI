import type { NextApiRequest, NextApiResponse } from "next";
import OpenAI from "openai";
import { verifyToken } from "../../utils/jwt";

// 🔐 Verifica se chave da OpenAI está presente
if (!process.env.OPENAI_API_KEY) {
  throw new Error("❌ OPENAI_API_KEY não está definida.");
}

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

type LanguageOptions =
  | "pt"
  | "en"
  | "es"
  | "fr"
  | "de"
  | "it"
  | "ru"
  | "hi"
  | "ar"
  | "zh"
  | "ja";

interface AIComboRequest {
  topic?: string;
  language?: LanguageOptions;
}

interface AIComboResponse {
  script: string;
  title: string;
  tags: string;
  description: string;
  language: string;
}

const languageMap: Record<LanguageOptions, string> = {
  pt: "em português",
  en: "in English",
  es: "en español",
  fr: "en français",
  de: "auf Deutsch",
  it: "in italiano",
  ru: "на русском",
  hi: "हिंदी में",
  ar: "بالعربية",
  zh: "用中文",
  ja: "日本語で",
};

const getAIText = async (
  messages: OpenAI.Chat.ChatCompletionMessageParam[]
): Promise<string> => {
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4",
      temperature: 0.7,
      messages,
    });
    return response.choices[0]?.message?.content?.trim() || "";
  } catch (err) {
    console.error("Erro ao chamar OpenAI:", err);
    return "";
  }
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<AIComboResponse | { error: string; details?: string }>
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

  const { topic, language = "pt" } = req.body as AIComboRequest;
  const langText = languageMap[language] || "em português";

  if (!topic || typeof topic !== "string") {
    return res
      .status(400)
      .json({ error: "O campo 'topic' é obrigatório e deve ser uma string." });
  }

  try {
    const [script, title, tags, description] = await Promise.all([
      getAIText([
        {
          role: "system",
          content:
            "Você é um especialista em criação de roteiros curtos para vídeos de redes sociais.",
        },
        {
          role: "user",
          content: `Crie um roteiro envolvente para um vídeo com o tema: ${topic}. Gere o roteiro ${langText}.`,
        },
      ]),
      getAIText([
        {
          role: "system",
          content:
            "Você é especialista em criar títulos curtos, impactantes e otimizados para vídeos.",
        },
        {
          role: "user",
          content: `Crie um título envolvente para um vídeo com o tema: ${topic}. Gere o título ${langText}.`,
        },
      ]),
      getAIText([
        {
          role: "system",
          content:
            "Você gera hashtags virais e otimizadas para vídeos de redes sociais.",
        },
        {
          role: "user",
          content: `Liste de 5 a 10 hashtags populares para um vídeo com o tema: ${topic}. Apenas as hashtags separadas por vírgula, ${langText}.`,
        },
      ]),
      getAIText([
        {
          role: "system",
          content:
            "Você cria descrições otimizadas, interessantes e com chamadas para ação.",
        },
        {
          role: "user",
          content: `Crie uma descrição envolvente para um vídeo com o tema: ${topic}. Gere a descrição ${langText}.`,
        },
      ]),
    ]);

    return res.status(200).json({
      script,
      title,
      tags,
      description,
      language,
    });
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : "Erro desconhecido";
    console.error("❌ Erro ao gerar combo IA:", errorMessage);
    return res
      .status(500)
      .json({ error: "Erro ao gerar conteúdo com IA", details: errorMessage });
  }
}
