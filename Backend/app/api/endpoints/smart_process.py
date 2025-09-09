# 📁 backend/app/api/endpoints/smart_process.py

import os
import logging
from uuid import uuid4
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from celery import chain

from app.config import settings
from app.tasks import (
    process_smart_video_cut_task as process_smart_video,
    transcribe_video_task,
    analyze_sentiment_task,
    cut_video_by_moments_task
)
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/smart-process")
logger = logging.getLogger(__name__)

# === 📦 SCHEMA ===

class SmartProcessResponse(BaseModel):
    task_id: str
    message: str

# === 🎥 ENDPOINT: Upload + Processamento Inteligente ===

@router.post(
    "/upload",
    response_model=SmartProcessResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["SmartProcess"]
)
async def trigger_smart_process_upload(
    file: UploadFile = File(...),
    use_scene_detection: Optional[bool] = Form(True),
    min_cut_duration: Optional[float] = Form(1.0, ge=0.5, le=30.0),
    max_cut_duration: Optional[float] = Form(10.0, ge=1.0, le=60.0),
    scene_threshold: Optional[float] = Form(20.0, ge=0.0, le=100.0),
    motion_threshold: Optional[float] = Form(20.0, ge=0.0, le=100.0),
    audio_peak_threshold: Optional[int] = Form(-20, ge=-100, le=0),
    max_num_cuts: Optional[int] = Form(5, ge=1, le=20),
    face_weight: Optional[float] = Form(0.5),
    object_weight: Optional[float] = Form(0.6),
    audio_weight: Optional[float] = Form(0.4),
    motion_weight: Optional[float] = Form(0.3),
    analyze_audio_advanced: Optional[bool] = Form(False),
    speech_weight: Optional[float] = Form(0.3),
    music_weight: Optional[float] = Form(0.2),
    frame_sample_rate_face_object: Optional[int] = Form(5, ge=1, le=30),
):
    """
    Recebe um vídeo e inicia o processo de corte inteligente com IA.
    """
    ext = Path(file.filename).suffix.lower().strip(".")
    if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
        logger.warning(f"Extensão inválida: {file.filename}")
        raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

    try:
        unique_filename = f"{uuid4()}.{ext}"
        file_path = os.path.join(settings.TMP_DIR, unique_filename)
        os.makedirs(settings.TMP_DIR, exist_ok=True)

        # ⚠️ Leitura segura (em blocos)
        with open(file_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                out_file.write(chunk)

        logger.info(f"📥 Upload recebido: {unique_filename} | Iniciando processamento inteligente...")

        task = process_smart_video.delay(
            file_path,
            use_scene_detection=use_scene_detection,
            min_cut_duration=min_cut_duration,
            max_cut_duration=max_cut_duration,
            scene_threshold=scene_threshold,
            motion_threshold=motion_threshold,
            audio_peak_threshold=audio_peak_threshold,
            max_num_cuts=max_num_cuts,
            face_weight=face_weight,
            object_weight=object_weight,
            audio_weight=audio_weight,
            motion_weight=motion_weight,
            analyze_audio_advanced=analyze_audio_advanced,
            speech_weight=speech_weight,
            music_weight=music_weight,
            frame_sample_rate_face_object=frame_sample_rate_face_object,
        )

        return SmartProcessResponse(task_id=task.id, message="Processamento inteligente de vídeo iniciado.")
    except Exception as e:
        logger.exception(f"❌ Erro ao processar vídeo inteligente: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar o vídeo.")

# === 🧠 ENDPOINT: Transcrição + Sentimento + Corte ===

@router.post(
    "/process-with-sentiment",
    response_model=SmartProcessResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["SmartProcess"]
)
async def process_video_with_sentiment(video_id: str = Form(...)):
    """
    Inicia um fluxo encadeado:
    - transcrição
    - análise de sentimento
    - corte com base nas emoções detectadas
    """
    video_path = os.path.join(settings.TMP_DIR, video_id)
    if not os.path.exists(video_path):
        logger.warning(f"📂 Vídeo não encontrado: {video_id}")
        raise HTTPException(status_code=404, detail="Vídeo não encontrado.")

    try:
        workflow = chain(
            transcribe_video_task.s(video_path),
            analyze_sentiment_task.s(),
            cut_video_by_moments_task.s(video_path)
        )
        result = workflow.delay()

        logger.info(f"🔗 Fluxo iniciado: {video_id} | Task ID: {result.id}")
        return SmartProcessResponse(task_id=result.id, message="Fluxo iniciado: transcrição → sentimento → corte.")
    except Exception as e:
        logger.exception(f"❌ Erro no fluxo com sentimento: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar o fluxo de IA com sentimento.")
