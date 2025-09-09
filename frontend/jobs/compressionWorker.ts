// 📁 jobs/compressionWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import fs from "fs";
import path from "path";

const execAsync = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

new Worker(
  "compression",
  async (job) => {
    const { jobId, targetSizeMb = 10 } = job.data;

    if (!jobId || typeof targetSizeMb !== "number") {
      console.error("❌ Dados inválidos para compressão:", job.data);
      return;
    }

    console.log(
      `🗜️ Iniciando compressão para job ${jobId}, alvo ≈${targetSizeMb}MB`
    );

    const input = path.resolve(__dirname, `../temp/${jobId}.mp4`);
    const outputDir = path.resolve(__dirname, "../output");
    const output = path.join(outputDir, `${jobId}-compressed.mp4`);

    if (!fs.existsSync(input)) {
      console.error(`❌ Arquivo de entrada não encontrado: ${input}`);
      return;
    }

    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const targetBitrateKbps = Math.floor((targetSizeMb * 8192) / 60); // ≈ 60s padrão

    const command = `ffmpeg -i "${input}" -b:v ${targetBitrateKbps}k -bufsize ${targetBitrateKbps}k -c:a copy "${output}"`;

    try {
      console.log(`▶️ Executando FFmpeg: ${command}`);
      await execAsync(command);
      console.log(`✅ Compressão concluída: ${output}`);
    } catch (err) {
      console.error(`❌ Erro na compressão do job ${jobId}:`, err);
    }
  },
  { connection }
);
