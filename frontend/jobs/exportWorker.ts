// 📁 jobs/exportWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import path from "path";
import fs from "fs";

const execAsync = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

new Worker(
  "export",
  async (job) => {
    const { jobId } = job.data;

    if (!jobId) {
      console.error("❌ jobId ausente no job de exportação.");
      return;
    }

    console.log(`📦 Finalizando exportação para o job ${jobId}`);

    const inputPath = path.resolve(__dirname, `../output/${jobId}-edited.mp4`);
    const outputPath = path.resolve(__dirname, `../output/${jobId}-final.mp4`);

    if (!fs.existsSync(inputPath)) {
      console.error(`❌ Arquivo de entrada não encontrado: ${inputPath}`);
      return;
    }

    const command = `ffmpeg -i "${inputPath}" -preset fast -crf 24 "${outputPath}"`;

    try {
      console.log(`▶️ Executando comando FFmpeg: ${command}`);
      await execAsync(command);
      console.log(`✅ Exportação finalizada para job ${jobId}: ${outputPath}`);
    } catch (error) {
      console.error(`❌ Erro ao exportar job ${jobId}:`, error);
    }
  },
  { connection }
);
