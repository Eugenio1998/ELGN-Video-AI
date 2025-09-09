// 📁 jobs/filterWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import fs from "fs";
import path from "path";

const execPromise = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

new Worker(
  "apply-filters",
  async (job) => {
    const { jobId, filters } = job.data;

    if (!jobId || !filters || !Array.isArray(filters) || filters.length === 0) {
      console.error("❌ Dados inválidos no job de filtro.");
      return;
    }

    console.log(`🎨 Aplicando filtros [${filters.join(", ")}] no job ${jobId}`);

    const inputPath = path.resolve(__dirname, `../temp/${jobId}.mp4`);
    const outputPath = path.resolve(
      __dirname,
      `../output/${jobId}-filtered.mp4`
    );

    if (!fs.existsSync(inputPath)) {
      console.error(`❌ Arquivo de entrada não encontrado: ${inputPath}`);
      return;
    }

    const filterString = filters.join(",");

    const command = `ffmpeg -i "${inputPath}" -vf "${filterString}" "${outputPath}"`;

    try {
      console.log(`▶️ Executando comando FFmpeg: ${command}`);
      await execPromise(command);
      console.log(`✅ Filtros aplicados com sucesso ao vídeo do job ${jobId}`);
    } catch (error) {
      console.error(`❌ Erro ao aplicar filtros no job ${jobId}:`, error);
    }
  },
  { connection }
);
