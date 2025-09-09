// 📁 jobs/adjustFormatWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import path from "path";
import fs from "fs";

const execPromise = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

type Format = "square" | "vertical" | "horizontal" | "landscape" | "portrait";

interface AdjustFormatData {
  jobId: string;
  targetFormat: Format;
}

// 🎯 Define escala e padding conforme formato desejado
function getFFmpegScaleFilter(format: Format): string {
  switch (format) {
    case "square":
      return "scale=720:720:force_original_aspect_ratio=decrease,pad=720:720:(ow-iw)/2:(oh-ih)/2";
    case "vertical":
    case "portrait":
      return "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2";
    case "horizontal":
    case "landscape":
    default:
      return "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2";
  }
}

new Worker<AdjustFormatData>(
  "adjust-format",
  async (job) => {
    const { jobId, targetFormat } = job.data || {};

    if (!jobId || !targetFormat) {
      console.error("❌ Dados ausentes no job: jobId ou targetFormat");
      return;
    }

    const inputPath = path.resolve(__dirname, `../temp/${jobId}.mp4`);
    const outputPath = path.resolve(
      __dirname,
      `../output/${jobId}-${targetFormat}.mp4`
    );

    if (!fs.existsSync(inputPath)) {
      console.error(`❌ Arquivo de entrada não encontrado: ${inputPath}`);
      return;
    }

    const scaleFilter = getFFmpegScaleFilter(targetFormat);
    const command = `ffmpeg -y -i "${inputPath}" -vf "${scaleFilter}" -c:a copy "${outputPath}"`;

    console.log(
      `🎞️ Ajustando vídeo do job ${jobId} para o formato '${targetFormat}'`
    );
    console.log(`▶️ Comando FFmpeg: ${command}`);

    try {
      await execPromise(command);
      console.log(`✅ Vídeo ajustado com sucesso: ${outputPath}`);
    } catch (error) {
      console.error(`❌ Erro ao ajustar vídeo do job ${jobId}:`, error);
    }
  },
  { connection }
);
