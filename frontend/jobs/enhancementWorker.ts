// 📁 jobs/enhancementWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import path from "path";
import fs from "fs";

const execPromise = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

new Worker(
  "enhancement",
  async (job) => {
    const { jobId } = job.data;

    if (!jobId) {
      console.error("❌ jobId ausente no job de enhancement.");
      return;
    }

    console.log(`🎛️ Aplicando melhorias de qualidade no job ${jobId}`);

    const inputPath = path.resolve(__dirname, `../temp/${jobId}.mp4`);
    const outputDir = path.resolve(__dirname, "../output");
    const outputPath = path.join(outputDir, `${jobId}-enhanced.mp4`);

    if (!fs.existsSync(inputPath)) {
      console.error(`❌ Arquivo de entrada não encontrado: ${inputPath}`);
      return;
    }

    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const cmd = `ffmpeg -i "${inputPath}" -vf "hqdn3d,scale=1280:720" "${outputPath}"`;

    try {
      console.log(`▶️ Executando comando: ${cmd}`);
      await execPromise(cmd);
      console.log(`✅ Melhoria aplicada ao vídeo do job ${jobId}`);
    } catch (error) {
      console.error(`❌ Erro ao aplicar enhancement no job ${jobId}:`, error);
    }
  },
  { connection }
);
