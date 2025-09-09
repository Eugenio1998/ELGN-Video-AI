// 📁 jobs/voiceWorker.ts

import { Worker } from "bullmq";
import IORedis from "ioredis";
import { exec } from "child_process";
import util from "util";

const execPromise = util.promisify(exec);
const connection = new IORedis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null,
});

new Worker(
  "voice",
  async (job) => {
    const { jobId, voiceType } = job.data;

    if (!jobId || !voiceType) {
      throw new Error("❌ Parâmetros 'jobId' e 'voiceType' são obrigatórios.");
    }

    console.log(`🗣️ Gerando voz tipo '${voiceType}' para job ${jobId}`);

    const outputPath = `./output/${jobId}-voice-${voiceType}.mp3`;

    // 🔧 Substitua com integração real (ex: ElevenLabs, OpenAI TTS)
    const ttsCommand = `echo "Texto gerado por IA (${voiceType})" | ffmpeg -f lavfi -i anullsrc -t 2 -q:a 9 -acodec libmp3lame "${outputPath}"`;

    try {
      await execPromise(ttsCommand);
      console.log(`✅ Voz '${voiceType}' gerada com sucesso: ${outputPath}`);
    } catch (err) {
      console.error(`❌ Erro ao gerar voz para job ${jobId}:`, err);
    }
  },
  { connection }
);
