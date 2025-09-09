// 📁 jobs/styleWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";

const execPromise = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

new Worker(
  "style",
  async (job) => {
    const { jobId, style } = job.data;

    if (!jobId || !style) {
      throw new Error("❌ Parâmetros ausentes: jobId e/ou style.");
    }

    console.log(`🎨 Aplicando estilo '${style}' ao vídeo do job ${jobId}`);

    const inputPath = `./temp/${jobId}.mp4`;
    const outputPath = `./output/${jobId}-styled-${style}.mp4`;

    const cmd = `ffmpeg -i "${inputPath}" -vf "hue=s=0,curves=preset=${style}" "${outputPath}"`;

    try {
      await execPromise(cmd);
      console.log(`✅ Estilo '${style}' aplicado ao job ${jobId}`);
    } catch (error) {
      console.error(
        `❌ Erro ao aplicar estilo '${style}' ao job ${jobId}:`,
        error
      );
    }
  },
  { connection }
);
