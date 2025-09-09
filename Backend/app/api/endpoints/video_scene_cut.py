# 📁 backend/app/api/endpoints/scene_cut.py

import os
import logging
from uuid import uuid4
from pathlib import Path
from shutil import copyfileobj

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.video_scene_cutter import detect_scenes_by_histogram
from app.config import settings
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/cut")
logger = logging.getLogger(__name__)

# === 🎬 Endpoint: Corte por Cena com OpenCV ===

@router.post(
    "/video/scene-detect",
    tags=["Video IA"],
    responses={
        500: {"model": ErrorResponse},
    }
)
async def detect_video_scenes(file: UploadFile = File(...)):
    """
    Detecta cortes automáticos de cena em um vídeo enviado usando análise de histograma.
    """
    try:
        logger.info(f"📥 Vídeo recebido para detecção de cenas: {file.filename}")

        # Criar caminho temporário
        ext = Path(file.filename).suffix or ".mp4"
        os.makedirs(settings.TMP_DIR, exist_ok=True)
        temp_path = os.path.join(settings.TMP_DIR, f"{uuid4()}{ext}")

        # Salvar arquivo temporário em chunks
        with open(temp_path, "wb") as f_out:
            while chunk := await file.read(1024 * 1024):
                f_out.write(chunk)

        logger.info(f"🔎 Analisando cenas com OpenCV: {temp_path}")
        scenes = detect_scenes_by_histogram(temp_path)

        # Limpar o arquivo
        if os.path.exists(temp_path):
            os.remove(temp_path)

        logger.info(f"✅ Cenas detectadas: {len(scenes)} cortes.")
        return {
            "filename": file.filename,
            "total_cuts": len(scenes),
            "scenes": scenes
        }

    except Exception as e:
        logger.exception(f"❌ Erro ao detectar cenas no vídeo: {e}")
        raise HTTPException(status_code=500, detail="Erro ao detectar cenas no vídeo.")
