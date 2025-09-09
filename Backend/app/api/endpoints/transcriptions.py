# 📁 backend/app/api/endpoints/transcriptions.py

import os
import logging
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.tasks import transcribe_video_task
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/transcriptions")
logger = logging.getLogger(__name__)

# === 📦 Schemas ===

class TranscriptionRequest(BaseModel):
    video_id: str = Field(..., description="Nome do vídeo existente no TMP_DIR")

class TranscriptionResponse(BaseModel):
    task_id: str = Field(..., description="ID da tarefa Celery iniciada")
    message: str = Field(..., description="Mensagem de status")

# === 📽️ Transcrição de vídeo existente ===

@router.post(
    "/",
    response_model=TranscriptionResponse,
    responses={500: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["Transcrição"]
)
async def request_transcription(request: TranscriptionRequest):
    """
    Inicia a transcrição de um vídeo já salvo localmente no TMP_DIR.
    """
    video_path = os.path.join(settings.TMP_DIR, request.video_id)
    if not os.path.exists(video_path):
        logger.warning(f"📂 Vídeo não encontrado: {request.video_id}")
        raise HTTPException(status_code=404, detail="Vídeo não encontrado.")

    try:
        task = transcribe_video_task.delay(video_path)
        logger.info(f"📤 Transcrição iniciada | Arquivo: {request.video_id} | Task ID: {task.id}")
        return TranscriptionResponse(task_id=task.id, message="Transcrição iniciada.")
    except Exception as e:
        logger.exception(f"Erro ao iniciar transcrição para {request.video_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar a transcrição.")

# === 📤 Upload + Transcrição ===

@router.post(
    "/upload",
    response_model=TranscriptionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Transcrição"]
)
async def request_transcription_upload(file: UploadFile = File(...)):
    """
    Faz upload de um vídeo e inicia transcrição automática.
    """
    ext = Path(file.filename).suffix.lower().strip(".")
    if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        logger.warning(f"Extensão inválida: {file.filename}")
        raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

    try:
        unique_filename = f"{uuid4()}.{ext}"
        file_path = os.path.join(settings.TMP_DIR, unique_filename)
        os.makedirs(settings.TMP_DIR, exist_ok=True)

        with open(file_path, "wb") as f_out:
            while chunk := await file.read(1024 * 1024):
                f_out.write(chunk)

        logger.info(f"📥 Upload recebido: {unique_filename}. Iniciando transcrição.")
        task = transcribe_video_task.delay(file_path)

        return TranscriptionResponse(
            task_id=task.id,
            message="Transcrição iniciada com sucesso."
        )
    except Exception as e:
        logger.exception(f"Erro ao processar vídeo para transcrição: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar o vídeo.")
