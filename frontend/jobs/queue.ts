import { Queue } from "bullmq";
import IORedis from "ioredis";

// ✅ Conexão única com Redis
const redisUrl = process.env.REDIS_URL;
if (!redisUrl) throw new Error("❌ Variável REDIS_URL não definida.");
export const connection = new IORedis(redisUrl);

// 🎯 Filas de processamento por tipo de tarefa

// 🎵 Áudio e Música
export const audioQueue = new Queue("audio", { connection });
export const voiceQueue = new Queue("voice", { connection });
export const addMusicQueue = new Queue("add-music", { connection });

// 🎥 Vídeo (formato, aspecto, cortes, resolução)
export const formatQueue = new Queue("adjust-format", { connection });
export const aspectRatioQueue = new Queue("aspect-ratio", { connection });
export const cutQueue = new Queue("apply-cuts", { connection });
export const resolutionQueue = new Queue("resolution", { connection });

// 🎨 Estilo e Filtros
export const filterQueue = new Queue("apply-filters", { connection });
export const styleQueue = new Queue("style", { connection });

// 🧼 Pós-processamento e otimização
export const enhancementQueue = new Queue("enhancement", { connection });
export const compressionQueue = new Queue("compression", { connection });
export const thumbnailQueue = new Queue("thumbnail", { connection });

// 📦 Exportação final
export const exportQueue = new Queue("export", { connection });
export const finalizeQueue = new Queue("finalize", { connection });
