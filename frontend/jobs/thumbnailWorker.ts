// 📁 jobs/thumbnailWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import fs from "fs";

const execAsync = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

new Worker(
  "thumbnail",
  async (job) => {
    const { jobId } = job.data;

    if (!jobId) {
      throw new Error("❌ Parâmetro 'jobId' ausente.");
    }

    console.log(`🖼️ Iniciando geração de thumbnail para o job ${jobId}`);

    const inputVideo = `./output/${jobId}-processed.mp4`;
    const outputImage = `./public/thumbnails/${jobId}.jpg`;

    if (!fs.existsSync(inputVideo)) {
      console.error(`❌ Arquivo de vídeo não encontrado: ${inputVideo}`);
      return;
    }

    const command = `ffmpeg -i "${inputVideo}" -ss 00:00:02.000 -vframes 1 "${outputImage}"`;

    try {
      await execAsync(command);
      console.log(`✅ Thumbnail gerada com sucesso: ${outputImage}`);
    } catch (err) {
      console.error(`❌ Erro ao gerar thumbnail para o job ${jobId}:`, err);
    }
  },
  { connection }
);
