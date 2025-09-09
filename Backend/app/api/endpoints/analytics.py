# 📁 backend/app/api/endpoints/analytics.py

import os
import logging
from fastapi import APIRouter, Form, Path, HTTPException, status
from celery.result import AsyncResult
from pydantic import BaseModel

from app.tasks import analyze_viewer_attention_task, suggest_edits_for_retention_task
from app.config import settings
from app.api.error_response import ErrorResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# === 🔷 Schemas ===

class TaskResponse(BaseModel):
    task_id: str
    message: str

# === 📊 Endpoint: Iniciar Análise de Atenção ===

@router.post(
    "/videos/{video_id}/analyze-attention/",
    response_model=TaskResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["Analytics"]
)
async def analyze_viewer_attention(
    video_id: str = Path(..., description="ID do vídeo para análise"),
    platform_api_url: str = Form(..., description="URL da API da plataforma"),
    api_key: str = Form(..., description="Chave de API da plataforma")
):
    """
    Inicia uma task Celery para analisar a atenção do espectador.
    """
    try:
        logger.info(f"🎯 Iniciando análise de atenção para o vídeo: {video_id}")
        task = analyze_viewer_attention_task.delay(video_id, platform_api_url, api_key)
        return TaskResponse(task_id=task.id, message="Análise de atenção iniciada.")
    except Exception as e:
        logger.exception(f"[{video_id}] Erro ao iniciar análise de atenção: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar análise de atenção.")

# === 🧠 Endpoint: Gerar Sugestões com Base em Retenção ===

@router.post(
    "/videos/{video_id}/suggest-retention-edits/",
    response_model=TaskResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Analytics"]
)
async def suggest_retention_edits(
    video_id: str = Path(..., description="ID do vídeo para sugerir edições"),
    attention_task_id: str = Form(..., description="ID da task de análise de atenção")
):
    """
    Gera sugestões de edição com base na task de atenção anterior.
    """
    try:
        result = AsyncResult(attention_task_id)

        if not result.ready():
            logger.warning(f"[{video_id}] Task {attention_task_id} ainda em processamento.")
            raise HTTPException(status_code=400, detail="A análise de atenção ainda não foi concluída.")

        if result.failed():
            logger.error(f"[{video_id}] Task {attention_task_id} falhou.")
            raise HTTPException(status_code=500, detail="A task de atenção falhou.")

        try:
            attention_data = result.get(timeout=30)
        except TimeoutError:
            logger.exception(f"[{video_id}] Timeout ao recuperar resultado da task {attention_task_id}")
            raise HTTPException(status_code=500, detail="Tempo excedido ao aguardar resultado da análise.")

        video_path = os.path.join(settings.UPLOAD_FOLDER, video_id)

        if not os.path.exists(video_path):
            logger.error(f"[{video_id}] Caminho do vídeo não encontrado: {video_path}")
            raise HTTPException(status_code=404, detail="Vídeo não encontrado no servidor.")

        task = suggest_edits_for_retention_task.delay(attention_data, video_path)
        logger.info(f"[{video_id}] Task de sugestão de edição iniciada: {task.id}")

        return TaskResponse(task_id=task.id, message="Sugestões de edição iniciadas.")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[{video_id}] Erro ao gerar sugestões de edição: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar sugestões de edição.")
