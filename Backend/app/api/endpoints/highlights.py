# 📁 backend/app/api/endpoints/highlights.py

import os
import logging
from uuid import uuid4
from pathlib import Path
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.tasks import generate_video_highlights_task
from app.config import settings
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/highlights")
logger = logging.getLogger(__name__)

# === 📦 Schema de Resposta ===

class HighlightResponse(BaseModel):
    task_id: str
    message: str

# === 🎬 Endpoint: Gerar Destaques de Vídeo Existente ===

@router.post(
    "/videos/{video_id}/generate",
    response_model=HighlightResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Destaques"]
)
async def generate_highlights(
    video_id: str,
    highlight_duration: int = Form(..., ge=5, le=300, description="Duração de cada destaque em segundos")
):
    """
    Gera destaques automáticos de um vídeo já existente no servidor.
    """
    video_path = os.path.join(settings.UPLOAD_FOLDER, video_id)
    if not os.path.exists(video_path):
        logger.warning(f"[{video_id}] Arquivo de vídeo não encontrado: {video_path}")
        raise HTTPException(status_code=404, detail="Vídeo não encontrado.")

    try:
        task = generate_video_highlights_task.delay(video_path, highlight_duration)
        logger.info(f"[{video_id}] Task iniciada | Duração: {highlight_duration}s | Task ID: {task.id}")
        return HighlightResponse(
            task_id=task.id,
            message=f"Geração de destaques iniciada para {video_id}."
        )
    except Exception as e:
        logger.exception(f"[{video_id}] Erro ao iniciar geração de destaques: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar destaques.")

# === 📤 Endpoint: Upload e Geração de Destaques ===

@router.post(
    "/upload-and-generate",
    response_model=HighlightResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Destaques"]
)
async def upload_and_generate_highlights(
    file: UploadFile = File(...),
    highlight_duration: int = Form(..., ge=5, le=300, description="Duração de cada destaque em segundos")
):
    """
    Faz upload de um vídeo e gera destaques automaticamente.
    """
    ext = Path(file.filename).suffix.lower().strip(".")
    if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        logger.warning(f"Extensão inválida: {file.filename} | Permitidos: {settings.ALLOWED_VIDEO_EXTENSIONS}")
        raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

    try:
        unique_filename = f"{uuid4()}.{ext}"
        video_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)

        # Garante que a pasta existe
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

        # ⚠️ Leitura mais segura para arquivos grandes
        with open(video_path, "wb") as f_out:
            while chunk := await file.read(1024 * 1024):  # lê em blocos de 1MB
                f_out.write(chunk)

        task = generate_video_highlights_task.delay(video_path, highlight_duration)
        logger.info(f"[{unique_filename}] Upload recebido | Task ID: {task.id} | Duração: {highlight_duration}s")
        return HighlightResponse(
            task_id=task.id,
            message=f"Upload recebido. Geração de destaques iniciada para {unique_filename}."
        )
    except Exception as e:
        logger.exception(f"Erro ao processar upload: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar o vídeo para destaques.")
