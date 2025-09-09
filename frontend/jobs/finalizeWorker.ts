// 📁 jobs/finalizeWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import fs from "fs";
import path from "path";

const execAsync = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

new Worker(
  "finalize",
  async (job) => {
    const { jobId, includeWatermark, format } = job.data;

    if (!jobId || !format) {
      console.error("❌ Dados inválidos no job de finalização.");
      return;
    }

    console.log(`🎬 Iniciando finalização do vídeo do job ${jobId}...`);

    const input = path.resolve(__dirname, `../output/${jobId}-processed.mp4`);
    const output = path.resolve(
      __dirname,
      `../output/final-${jobId}.${format}`
    );
    const watermarkPath = path.resolve(__dirname, "../assets/logo.png");

    if (!fs.existsSync(input)) {
      console.error(`❌ Arquivo de entrada não encontrado: ${input}`);
      return;
    }

    let ffmpegCommand = "";

    if (includeWatermark) {
      if (!fs.existsSync(watermarkPath)) {
        console.error(
          `❌ Arquivo de watermark não encontrado: ${watermarkPath}`
        );
        return;
      }

      ffmpegCommand = `ffmpeg -i "${input}" -i "${watermarkPath}" -filter_complex "overlay=10:10" -c:v libx264 -preset fast "${output}"`;
    } else {
      ffmpegCommand = `ffmpeg -i "${input}" -c:v libx264 -preset fast "${output}"`;
    }

    try {
      console.log(`▶️ Executando comando FFmpeg: ${ffmpegCommand}`);
      await execAsync(ffmpegCommand);
      console.log(`✅ Vídeo finalizado para job ${jobId}: ${output}`);
    } catch (error) {
      console.error(`❌ Erro na finalização do job ${jobId}:`, error);
    }
  },
  { connection }
);
