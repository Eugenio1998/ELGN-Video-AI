// 📁 pages/api/transcribe-audio.ts

import type { NextApiRequest, NextApiResponse } from "next";
import formidable, { File } from "formidable";
import fs from "fs";
import { verifyToken } from "../../utils/verifyToken";

export const config = {
  api: {
    bodyParser: false,
  },
};

type SuccessResponse = {
  success: true;
  jobId: string;
  transcription: string;
};

type ErrorResponse = {
  error: string;
  details?: string;
};

const supportedLanguages = [
  "pt",
  "en",
  "es",
  "fr",
  "de",
  "it",
  "ru",
  "hi",
  "ar",
  "zh",
  "ja",
];

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<SuccessResponse | ErrorResponse>
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ error: "Método não permitido" });
  }

  const token = req.headers.authorization?.split(" ")[1];
  if (!token || !verifyToken(token)) {
    return res.status(401).json({ error: "Não autorizado" });
  }

  const form = new formidable.IncomingForm({
    keepExtensions: true,
    maxFileSize: 100 * 1024 * 1024, // 100MB
  });

  form.parse(req, async (err, fields, files) => {
    if (err) {
      console.error("Erro ao processar o upload:", err);
      return res.status(500).json({ error: "Erro no upload do arquivo." });
    }

    const jobId = fields.jobId?.toString();
    const language = fields.language?.toString() || "pt";

    if (!jobId) {
      return res.status(400).json({ error: "Campo 'jobId' é obrigatório." });
    }

    if (!supportedLanguages.includes(language)) {
      return res.status(400).json({
        error: "Idioma não suportado",
        details: `Idiomas aceitos: ${supportedLanguages.join(", ")}`,
      });
    }

    const audioFile = Array.isArray(files.audio)
      ? files.audio[0]
      : (files.audio as File | undefined);

    if (!audioFile || !audioFile.filepath) {
      return res.status(400).json({ error: "Arquivo de áudio ausente." });
    }

    try {
      const formData = new FormData();
      formData.append(
        "file",
        fs.createReadStream(audioFile.filepath) as unknown as Blob
      );
      formData.append("model", "whisper-1");
      formData.append("language", language);

      const response = await fetch(
        "https://api.openai.com/v1/audio/transcriptions",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${process.env.OPENAI_API_KEY as string}`,
          },
          body: formData,
        }
      );

      const data: { text?: string; error?: { message?: string } } =
        await response.json();

      if (!response.ok || !data.text) {
        console.error("Erro na transcrição:", data.error?.message);
        return res.status(500).json({
          error: "Erro ao transcrever",
          details: data.error?.message || "Erro desconhecido.",
        });
      }

      return res.status(200).json({
        success: true,
        jobId,
        transcription: data.text,
      });
    } catch (error) {
      const err = error as Error;
      console.error("Erro interno:", err.message);
      return res.status(500).json({
        error: "Erro interno na transcrição",
        details: err.message,
      });
    }
  });
}
