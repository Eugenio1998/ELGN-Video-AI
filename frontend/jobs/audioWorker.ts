// 📁 jobs/audioWorker.ts

import { Worker, Job } from "bullmq";
import { exec } from "child_process";
import util from "util";
import { audioQueue } from "./queue";
import fs from "fs";
import path from "path";

const execAsync = util.promisify(exec);

// 🎯 Tipagem do job de áudio
type AudioJobData = {
  prompt: string;
  type: "music" | "voice";
  genre?: string;
  voiceId?: string;
  language?: string;
  emotion?: string;
  duration?: number;
};

new Worker("audio", async (job: Job<AudioJobData>) => {
  const {
    prompt,
    type,
    genre,
    voiceId,
    language,
    emotion,
    duration = 10,
  } = job.data;

  if (!prompt || !type) {
    console.error(
      "❌ Job de áudio inválido: 'prompt' e 'type' são obrigatórios."
    );
    return;
  }

  const outputDir = path.resolve(__dirname, "../public/output");
  const outputPath = path.join(outputDir, `audio-${job.id}.mp3`);

  // Cria pasta se não existir
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  try {
    console.log(`🎧 Processando áudio '${type}' para prompt: "${prompt}"`);

    // 🔁 Simulação com FFmpeg (substituir por geração real no futuro)
    if (type === "music") {
      console.log(`🎼 Gênero musical: ${genre || "não especificado"}`);
    } else {
      console.log(
        `🗣️ Voz: ${voiceId || "padrão"} | Idioma: ${
          language || "pt"
        } | Emoção: ${emotion || "neutra"}`
      );
    }

    await execAsync(
      `echo "${prompt}" | ffmpeg -f lavfi -i anullsrc -t ${duration} -q:a 9 -acodec libmp3lame "${outputPath}"`
    );

    console.log(`✅ Áudio gerado com sucesso: ${outputPath}`);

    // ➕ Task subsequente simulada
    await audioQueue.add("followup-task", {
      parentJobId: job.id,
      step: "normalize-volume",
    });
  } catch (error) {
    console.error(`❌ Erro ao gerar áudio para job ${job.id}:`, error);
  }
});
