// 📁 jobs/aspectRatioWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import path from "path";
import fs from "fs";

const execPromise = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

interface AspectRatioData {
  jobId: string;
  aspectRatio: string;
}

new Worker<AspectRatioData>(
  "aspect-ratio",
  async (job) => {
    const { jobId, aspectRatio } = job.data || {};

    if (!jobId || !aspectRatio) {
      console.error(
        "❌ Dados incompletos no job: jobId ou aspectRatio ausente."
      );
      return;
    }

    const inputPath = path.resolve(__dirname, `../temp/${jobId}.mp4`);
    const outputPath = path.resolve(__dirname, `../output/${jobId}-aspect.mp4`);

    if (!fs.existsSync(inputPath)) {
      console.error(`❌ Arquivo de entrada não encontrado: ${inputPath}`);
      return;
    }

    const cmd = `ffmpeg -i "${inputPath}" -aspect ${aspectRatio} -c:a copy "${outputPath}"`;

    console.log(`🎞️ Aplicando aspecto ${aspectRatio} no vídeo do job ${jobId}`);
    console.log(`▶️ Executando FFmpeg: ${cmd}`);

    try {
      await execPromise(cmd);
      console.log(
        `✅ Aspecto '${aspectRatio}' aplicado com sucesso: ${outputPath}`
      );
    } catch (error) {
      console.error(
        `❌ Erro ao aplicar aspecto no vídeo do job ${jobId}:`,
        error
      );
    }
  },
  { connection }
);
