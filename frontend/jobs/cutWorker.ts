// 📁 jobs/cutWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import fs from "fs";
import path from "path";

const execPromise = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

new Worker(
  "apply-cuts",
  async (job) => {
    const { jobId } = job.data;

    if (!jobId) {
      console.error("❌ jobId ausente no job de cortes.");
      return;
    }

    console.log(`✂️ Executando IA de cortes para job ${jobId}`);

    const inputPath = path.resolve(__dirname, `../temp/${jobId}.mp4`);
    const outputDir = path.resolve(__dirname, "../output");
    const outputPath = path.join(outputDir, `${jobId}-cut.mp4`);

    if (!fs.existsSync(inputPath)) {
      console.error(`❌ Arquivo de entrada não encontrado: ${inputPath}`);
      return;
    }

    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Simulação de corte fixo (2s a 7s)
    const cmd = `ffmpeg -i "${inputPath}" -ss 00:00:02 -t 00:00:05 -c:a copy "${outputPath}"`;

    try {
      console.log(`▶️ Executando comando: ${cmd}`);
      await execPromise(cmd);
      console.log(`✅ Cortes aplicados com sucesso ao job ${jobId}`);
    } catch (error) {
      console.error(`❌ Erro ao aplicar cortes no job ${jobId}:`, error);
    }
  },
  { connection }
);
