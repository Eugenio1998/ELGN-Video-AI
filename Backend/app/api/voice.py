import logging
from fastapi import APIRouter, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr
from typing import Literal

from app.services.voice_generator import generate_voice
from app.services.audit_logging import log_event
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/voice", tags=["Voice"])
logger = logging.getLogger(__name__)

# === 🔊 SCHEMA DE RESPOSTA ===

class VoiceResponse(BaseModel):
    message: str
    audio_url: str

# === 🎤 ENDPOINT: Geração de voz com IA ===

@router.post(
    "/generate",
    response_model=VoiceResponse,
    responses={
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
def generate_voice_route(
    text: constr(min_length=3) = Form(...),
    lang: Literal["pt", "en", "es", "fr", "de"] = Form("pt"),
    provider: Literal["gtts", "elevenlabs", "openai"] = Form("gtts"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gera uma voz artificial com base em texto e provedor especificado.
    Requer autenticação.
    """
    try:
        logger.info(f"🗣️ Gerando voz para o usuário {current_user.username} com o provedor {provider}")

        audio_url = generate_voice(text, lang=lang, provider=provider)

        log_event(current_user.id, f"Gerou voz com IA ({provider})", db)

        logger.info(f"✅ Voz gerada com sucesso para {current_user.username}")

        return VoiceResponse(
            message="Voz gerada com sucesso!",
            audio_url=audio_url
        )

    except Exception as e:
        logger.error(f"❌ Erro ao gerar voz para {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar a voz.")
