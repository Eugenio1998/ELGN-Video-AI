import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";

const execPromise = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!);

// 🎯 Mapeamento de resoluções padrão
const resolutionMap: Record<string, string> = {
  "480p": "640:480",
  "720p": "1280:720",
  "1080p": "1920:1080",
  "2k": "2560:1440",
  "4k": "3840:2160",
};

new Worker(
  "resolution",
  async (job) => {
    const { jobId, resolution } = job.data;

    if (!jobId || !resolution) {
      throw new Error("❌ Parâmetros ausentes para aplicação de resolução.");
    }

    const size = resolutionMap[resolution] || "1920:1080";

    console.log(
      `📐 Aplicando resolução ${resolution} (${size}) ao job ${jobId}`
    );

    const command = `ffmpeg -i ./temp/${jobId}.mp4 -vf scale=${size} ./output/${jobId}-res-${resolution}.mp4`;

    try {
      await execPromise(command);
      console.log(
        `✅ Resolução ${resolution} aplicada ao vídeo do job ${jobId}`
      );
    } catch (error) {
      console.error(`❌ Erro ao aplicar resolução no job ${jobId}:`, error);
    }
  },
  { connection }
);
