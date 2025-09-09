# 📁 backend/app/api/endpoints/voice.py

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr

from app.tasks import generate_voice_task
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/voice", tags=["Voz IA"])
logger = logging.getLogger(__name__)

# === 📦 SCHEMAS ===

class VoiceRequest(BaseModel):
    text: constr(min_length=3)
    language: Literal["pt", "en", "es", "fr", "de"] = "pt"
    voice_model: Literal["elevenlabs", "openai", "gtts"] = "elevenlabs"
    output_format: Literal["mp3", "wav", "ogg"] = "mp3"

class VoiceGenerationResponse(BaseModel):
    task_id: str
    message: str

# === 🗣️ GERAÇÃO DE VOZ VIA IA ===

@router.post(
    "/generate",
    response_model=VoiceGenerationResponse,
    responses={500: {"model": ErrorResponse}},
)
async def generate_speech(request: VoiceRequest):
    """
    Gera áudio a partir de um texto usando IA (modelos: elevenlabs, openai, gTTS).
    """
    try:
        logger.info(f"🔊 Gerando voz com {request.voice_model} | Texto: {request.text[:30]}...")
        task = generate_voice_task.delay(
            request.text,
            request.language,
            request.voice_model,
            request.output_format
        )
        return VoiceGenerationResponse(
            task_id=task.id,
            message="Geração de voz iniciada."
        )
    except Exception as e:
        logger.exception(f"❌ Erro ao iniciar geração de voz: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar geração de voz.")
