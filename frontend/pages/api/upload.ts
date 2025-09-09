// 📁 pages/api/upload.ts

import type { NextApiRequest, NextApiResponse } from "next";
import formidable, { Part } from "formidable";
import fs from "fs";
import path from "path";
import { v4 as uuidv4 } from "uuid";
import { verifyToken } from "../../utils/verifyToken";

type UploadResponse = {
  success: true;
  jobId: string;
  filename: string;
  music: string | null;
  url: string;
  musicUrl: string | null;
};

type ErrorResponse = { error: string };

export const config = {
  api: { bodyParser: false },
};

const uploadDir = path.join(process.cwd(), "public", "uploads");
fs.mkdirSync(uploadDir, { recursive: true });

const allowedExtensions = [".mp4", ".mov", ".avi", ".mp3", ".wav"];

// 🔄 Promisifica o parse
function parseForm(
  req: NextApiRequest
): Promise<{ fields: formidable.Fields; files: formidable.Files }> {
  const form = formidable({
    multiples: false,
    uploadDir,
    keepExtensions: true,
    maxFileSize: 500 * 1024 * 1024,
    filter: (part: Part) => {
      const ext = path.extname(part.originalFilename || "").toLowerCase();
      const isValid = allowedExtensions.includes(ext);
      if (!isValid) {
        console.warn(`🚫 Upload rejeitado: extensão inválida (${ext})`);
      }
      return isValid;
    },
  });

  return new Promise((resolve, reject) => {
    form.parse(req, (err, fields, files) => {
      if (err) return reject(err);
      resolve({ fields, files });
    });
  });
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<UploadResponse | ErrorResponse>
) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ error: "Método não permitido" });
  }

  const rawHeader = req.headers.authorization;
  const token = rawHeader?.split(" ")[1];
  console.log("🔐 Authorization header:", rawHeader);
  console.log("🔐 Token extraído:", token);

  const user = token && verifyToken(token);
  if (!user) return res.status(401).json({ error: "Não autorizado" });

  try {
    const { files } = await parseForm(req);

    const uploadedFile = Array.isArray(files.file) ? files.file[0] : files.file;
    if (!uploadedFile || !uploadedFile.filepath) {
      return res.status(400).json({ error: "Arquivo de vídeo é obrigatório." });
    }

    const musicFile = Array.isArray(files.music) ? files.music[0] : files.music;

    const jobId = uuidv4();
    const originalName = uploadedFile.originalFilename || "";
    const ext = path.extname(originalName);
    const finalName = `${uuidv4()}${ext}`;
    const finalPath = path.join(uploadDir, finalName);
    fs.renameSync(uploadedFile.filepath, finalPath);
    const musicname = musicFile?.filepath
      ? path.basename(musicFile.filepath)
      : null;

    console.log(`📦 Upload feito por: ${user.email || "usuário desconhecido"}`);
    console.log("🎬 Vídeo recebido:", finalName);
    if (musicname) console.log("🎵 Música adicional:", musicname);

    return res.status(200).json({
      success: true,
      jobId,
      filename: finalName,
      music: musicname,
      url: `/uploads/${finalName}`,
      musicUrl: musicname ? `/uploads/${musicname}` : null,
    });
  } catch (error) {
    console.error("❌ Erro ao processar upload:", error);
    return res
      .status(500)
      .json({ error: "Erro inesperado ao processar upload." });
  }
}
