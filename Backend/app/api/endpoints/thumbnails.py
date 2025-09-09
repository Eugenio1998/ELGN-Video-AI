# 📁 backend/app/api/endpoints/thumbnails.py

import os
import logging
from uuid import uuid4
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from app.tasks import generate_intelligent_thumbnail_task
from app.config import settings
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/thumbnails")
logger = logging.getLogger(__name__)

# === 📦 Schema de Resposta ===

class ThumbnailTaskResponse(BaseModel):
    task_id: str = Field(..., description="ID da tarefa Celery iniciada")
    message: str = Field(..., description="Mensagem de status")

# === 📽️ Endpoint: Gerar thumbnail de vídeo já existente ===

@router.post(
    "/videos/{video_id}/generate",
    response_model=ThumbnailTaskResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Thumbnails"]
)
async def generate_thumbnail(video_id: str):
    """
    Gera thumbnail inteligente a partir de vídeo existente no TMP_DIR.
    """
    video_path = os.path.join(settings.TMP_DIR, video_id)
    if not os.path.exists(video_path):
        logger.warning(f"[{video_id}] Vídeo não encontrado no TMP_DIR.")
        raise HTTPException(status_code=404, detail="Vídeo não encontrado.")

    try:
        task = generate_intelligent_thumbnail_task.delay(video_path)
        logger.info(f"[{video_id}] Task de thumbnail iniciada | Task ID: {task.id}")
        return ThumbnailTaskResponse(
            task_id=task.id,
            message=f"Geração de thumbnail iniciada para {video_id}."
        )
    except Exception as e:
        logger.exception(f"[{video_id}] Erro ao iniciar thumbnail: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar thumbnail.")

# === 📤 Endpoint: Upload + geração automática de thumbnail ===

@router.post(
    "/upload-and-generate",
    response_model=ThumbnailTaskResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Thumbnails"]
)
async def upload_and_generate_thumbnail(file: UploadFile = File(...)):
    """
    Faz upload de um vídeo e gera thumbnail inteligente automaticamente.
    """
    ext = Path(file.filename).suffix.lower().strip(".")
    if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        logger.warning(f"Extensão não suportada: {file.filename}")
        raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

    try:
        unique_filename = f"{uuid4()}.{ext}"
        video_path = os.path.join(settings.TMP_DIR, unique_filename)
        os.makedirs(settings.TMP_DIR, exist_ok=True)

        # ⚠️ Leitura segura em blocos
        with open(video_path, "wb") as f_out:
            while chunk := await file.read(1024 * 1024):
                f_out.write(chunk)

        logger.info(f"[{unique_filename}] Upload recebido. Iniciando geração de thumbnail...")
        task = generate_intelligent_thumbnail_task.delay(video_path)

        return ThumbnailTaskResponse(
            task_id=task.id,
            message=f"Upload recebido. Geração de thumbnail iniciada para {unique_filename}."
        )

    except Exception as e:
        logger.exception(f"Erro ao processar vídeo para thumbnail: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar thumbnail.")
