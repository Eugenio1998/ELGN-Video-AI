// 📁 pages/api/list.ts

import type { NextApiRequest, NextApiResponse } from "next";
import fs from "fs";
import path from "path";
import { verifyToken } from "../../utils/verifyToken";

type VideoItem = {
  filename: string;
  url: string;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<VideoItem[] | { error: string }>
) {
  if (req.method !== "GET") {
    res.setHeader("Allow", ["GET"]);
    return res.status(405).json({ error: "Método não permitido" });
  }

  const token = req.headers.authorization?.split(" ")[1];
  const user = token && verifyToken(token);
  if (!user) {
    return res.status(401).json({ error: "Não autorizado." });
  }

  const uploadDir = path.join(process.cwd(), "public", "uploads");
  if (!fs.existsSync(uploadDir)) {
    return res.status(200).json([]);
  }

  const files = fs
    .readdirSync(uploadDir)
    .filter((f) => f.match(/\.(mp4|mov|avi)$/i));

  const videos = files.map((filename) => ({
    filename,
    url: `/uploads/${filename}`,
  }));

  return res.status(200).json(videos);
}
