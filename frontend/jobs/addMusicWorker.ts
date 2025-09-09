// 📁 jobs/addMusicWorker.ts
import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";
import path from "path";

const execPromise = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

new Worker(
  "add-music",
  async (job) => {
    const { jobId, musicUrl } = job.data || {};

    if (!jobId || !musicUrl) {
      console.error("❌ Dados ausentes no job: jobId ou musicUrl");
      return;
    }

    const inputPath = path.resolve(`./temp/${jobId}.mp4`);
    const outputPath = path.resolve(`./output/${jobId}-final.mp4`);

    const command = `ffmpeg -i "${inputPath}" -i "${musicUrl}" -filter_complex "[0:a][1:a]amix=inputs=2:duration=shortest" -y "${outputPath}"`;

    console.log(`🎬 Executando FFmpeg para o job ${jobId}`);
    try {
      await execPromise(command);
      console.log(`✅ Música inserida com sucesso: ${outputPath}`);
    } catch (error) {
      console.error(`❌ Erro ao processar job ${jobId}:`, error);
    }
  },
  { connection }
);
