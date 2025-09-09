# 📁 backend/app/services/transcription.py

import os
import uuid
import subprocess
import logging
from typing import Literal, Dict, Union
from fastapi import HTTPException
from functools import lru_cache
import whisper

# === 🛠️ Logger Nomeado ===
logger = logging.getLogger("transcription_service")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TMP_DIR = "/tmp"

# === 🧠 Carregar Modelo Whisper (Cacheado) ===
@lru_cache(maxsize=1)
def get_whisper_model():
    model_name = os.getenv("WHISPER_MODEL", "base")
    logger.info(f"📦 Carregando modelo Whisper: '{model_name}'...")
    try:
        model = whisper.load_model(model_name)
        logger.info(f"✅ Modelo Whisper '{model_name}' carregado com sucesso.")
        return model
    except Exception as e:
        logger.exception(f"❌ Erro ao carregar modelo Whisper: {e}")
        raise HTTPException(status_code=500, detail="Erro ao carregar modelo Whisper.")

# === 🎧 Extrair Áudio de Vídeo ===
def extract_audio_from_video(video_path: str) -> str:
    if not os.path.isfile(video_path):
        logger.error(f"🚫 Arquivo de vídeo não encontrado: {video_path}")
        raise HTTPException(status_code=400, detail="Arquivo de vídeo não encontrado.")

    audio_path = os.path.join(TMP_DIR, f"audio_{uuid.uuid4()}.mp3")
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "libmp3lame", "-ar", "16000", "-ac", "1", audio_path
    ]

    logger.info(f"🎙️ Extraindo áudio: '{video_path}' → '{audio_path}'...")
    try:
        subprocess.run(command, check=True, capture_output=True)
        logger.info(f"✅ Áudio extraído com sucesso: '{audio_path}'")
        return audio_path
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode("utf-8", errors="ignore")
        logger.error(f"❌ Erro no ffmpeg: {error_output}")
        raise HTTPException(status_code=500, detail="Erro ao extrair áudio do vídeo.")
    except FileNotFoundError:
        logger.error("❌ ffmpeg não encontrado. Verifique a instalação.")
        raise HTTPException(status_code=500, detail="ffmpeg não instalado ou fora do PATH.")

# === 📝 Transcrever Áudio ===
def transcribe_audio(audio_path: str, output_format: Literal["json", "srt"] = "json") -> Dict[str, Union[str, list]]:
    logger.info(f"🧠 Iniciando transcrição (formato: {output_format}) do áudio '{audio_path}'")
    try:
        result = get_whisper_model().transcribe(audio_path, fp16=False)
        logger.info("✅ Transcrição concluída.")

        if output_format == "json":
            return {
                "text": result["text"].strip(),
                "segments": result["segments"]
            }

        elif output_format == "srt":
            srt_content = ""
            for i, segment in enumerate(result["segments"], start=1):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                text = segment["text"].strip()
                srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
            return {"srt": srt_content}

        logger.error(f"🚫 Formato inválido solicitado: {output_format}")
        raise HTTPException(status_code=400, detail="Formato de saída inválido.")
    except Exception as e:
        logger.exception(f"❌ Erro na transcrição: {e}")
        raise HTTPException(status_code=500, detail="Erro ao transcrever áudio.")

# === ⏱️ Formatador de Timestamps ===
def format_timestamp(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

# === 🎬 Função Principal: Transcrever Vídeo ===
def transcribe_video(file_path: str, format: Literal["json", "srt"] = "json") -> Dict[str, Union[str, list]]:
    logger.info(f"🎬 Transcrevendo vídeo: '{file_path}' (formato: '{format}')")
    audio_path = extract_audio_from_video(file_path)

    try:
        result = transcribe_audio(audio_path, output_format=format)
    finally:
        try:
            os.remove(audio_path)
            logger.info(f"🧹 Áudio temporário removido: {audio_path}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao remover áudio temporário: {e}")

    logger.info(f"✅ Transcrição do vídeo '{file_path}' finalizada.")
    return result
