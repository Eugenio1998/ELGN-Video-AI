# 📁 app/utils/video_tools.py

import json
import logging
import os
import shutil
import subprocess
from fractions import Fraction
from uuid import uuid4

from fastapi import HTTPException

logger = logging.getLogger("video_tools")
TMP_DIR = "/tmp/elgn_ai_temp"


# === 🔍 Verifica se ffmpeg e ffprobe estão instalados ===
def _check_dependencies() -> None:
    for tool in ["ffmpeg", "ffprobe"]:
        if not shutil.which(tool):
            logger.error(f"❌ {tool} não está instalado no sistema.")
            raise HTTPException(
                status_code=500,
                detail=f"{tool} não está instalado no servidor.",
            )


# === 📁 Verifica existência de arquivo ===
def _check_file_exists(path: str) -> None:
    if not os.path.isfile(path):
        logger.warning(f"⚠️ Arquivo não encontrado: {path}")
        raise HTTPException(
            status_code=404, detail=f"Arquivo não encontrado: {path}"
        )


# === 🎵 Extrai o áudio de um vídeo ===
def extract_audio(video_path: str, output_format: str = "mp3") -> str:
    _check_dependencies()
    _check_file_exists(video_path)

    os.makedirs(f"{TMP_DIR}/audio", exist_ok=True)
    output_path = f"{TMP_DIR}/audio/audio_{uuid4()}.{output_format}"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "libmp3lame",
        "-ar",
        "16000",
        "-ac",
        "1",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao extrair áudio: {e}")
        raise HTTPException(
            status_code=500, detail="Erro ao extrair áudio do vídeo."
        )


# === 🖼️ Gera uma thumbnail do vídeo ===
def generate_thumbnail(video_path: str, timestamp: float = 1.0) -> str:
    _check_dependencies()
    _check_file_exists(video_path)

    os.makedirs(f"{TMP_DIR}/thumb", exist_ok=True)
    output_path = f"{TMP_DIR}/thumb/thumb_{uuid4()}.jpg"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-ss",
        str(timestamp),
        "-vframes",
        "1",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao gerar thumbnail: {e}")
        raise HTTPException(
            status_code=500, detail="Erro ao gerar thumbnail do vídeo."
        )


# === ✂️ Corta um trecho do vídeo ===
def cut_video_segment(video_path: str, start: float, duration: float) -> str:
    _check_dependencies()
    _check_file_exists(video_path)

    os.makedirs(f"{TMP_DIR}/cuts", exist_ok=True)
    output_path = f"{TMP_DIR}/cuts/clip_{uuid4()}.mp4"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-ss",
        str(start),
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao cortar vídeo: {e}")
        raise HTTPException(status_code=500, detail="Erro ao cortar o vídeo.")


# === 🗜️ Comprime o vídeo ===
def compress_video(video_path: str) -> str:
    _check_dependencies()
    _check_file_exists(video_path)

    os.makedirs(f"{TMP_DIR}/compressed", exist_ok=True)
    output_path = f"{TMP_DIR}/compressed/compressed_{uuid4()}.mp4"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vcodec",
        "libx265",
        "-crf",
        "28",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao comprimir vídeo: {e}")
        raise HTTPException(
            status_code=500, detail="Erro ao comprimir o vídeo."
        )


# === 📊 Extrai metadados do vídeo ===
def get_video_metadata(video_path: str) -> dict:
    _check_dependencies()
    _check_file_exists(video_path)

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate,duration",
        "-of",
        "json",
        video_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        metadata = json.loads(result.stdout)
        stream = metadata.get("streams", [{}])[0]

        return {
            "width": stream.get("width"),
            "height": stream.get("height"),
            "duration": float(stream.get("duration", 0)),
            "fps": float(Fraction(stream.get("r_frame_rate", "0/1"))),
        }

    except (
        subprocess.CalledProcessError,
        ValueError,
        KeyError,
        IndexError,
    ) as e:
        logger.error(f"❌ Erro ao obter metadados: {e}")
        raise HTTPException(
            status_code=500, detail="Erro ao obter metadados do vídeo."
        )


# === 📦 Exportações explícitas ===
__all__ = [
    "extract_audio",
    "generate_thumbnail",
    "cut_video_segment",
    "compress_video",
    "get_video_metadata",
]
