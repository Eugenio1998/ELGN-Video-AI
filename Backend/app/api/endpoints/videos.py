# 📁 backend/app/api/endpoints/videos.py

import os
import logging
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pydantic import BaseModel, Field

from app.config import settings
from app.tasks import process_smart_video_cut_task as process_smart_video
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/videos")
logger = logging.getLogger(__name__)

# === 📦 Schemas ===

class VideoUploadResponse(BaseModel):
    filename: str = Field(..., description="Nome único do vídeo salvo")
    message: str = Field(..., description="Mensagem de status")

class SmartProcessResponse(BaseModel):
    task_id: str = Field(..., description="ID da tarefa Celery")
    message: str = Field(..., description="Mensagem de status")

# === 🎥 Upload de vídeo com limite de 50MB ===

@router.post(
    "/",
    response_model=VideoUploadResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Vídeos"]
)
async def upload_video(request: Request, file: UploadFile = File(...)):
    """
    Faz upload de um vídeo com validação de tamanho (máx. 50MB) e extensão suportada.
    """
    max_size = 50 * 1024 * 1024  # 50MB
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        logger.warning("📛 Upload bloqueado: arquivo excede 50MB.")
        raise HTTPException(status_code=413, detail="Arquivo excede o limite de 50MB.")

    ext = Path(file.filename).suffix.lower().strip(".")
    if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        logger.warning(f"📛 Formato não suportado: {file.filename}")
        raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

    try:
        unique_filename = f"{uuid4()}.{ext}"
        file_path = os.path.join(settings.TMP_DIR, unique_filename)
        os.makedirs(settings.TMP_DIR, exist_ok=True)

        with open(file_path, "wb") as f_out:
            while chunk := await file.read(1024 * 1024):
                f_out.write(chunk)

        logger.info(f"📁 Upload concluído: {unique_filename}")
        return VideoUploadResponse(
            filename=unique_filename,
            message="Upload concluído com sucesso."
        )
    except Exception as e:
        logger.exception(f"❌ Erro ao salvar vídeo: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar o vídeo.")

# === 🧠 Processamento inteligente de vídeo existente ===

@router.post(
    "/{video_id}/smart-process",
    response_model=SmartProcessResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Vídeos"]
)
async def trigger_smart_process(video_id: str):
    """
    Inicia o processamento inteligente de um vídeo salvo no TMP_DIR.
    """
    video_path = os.path.join(settings.TMP_DIR, video_id)
    if not os.path.exists(video_path):
        logger.warning(f"📂 Vídeo não encontrado: {video_id}")
        raise HTTPException(status_code=404, detail="Vídeo não encontrado.")

    try:
        task = process_smart_video.delay(video_path)
        logger.info(f"🧠 Task iniciada para {video_id} | Task ID: {task.id}")
        return SmartProcessResponse(
            task_id=task.id,
            message="Processamento inteligente iniciado."
        )
    except Exception as e:
        logger.exception(f"Erro ao iniciar task de processamento: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar o processamento do vídeo.")
