# 📁 backend/app/api/endpoints/runway.py

import os
import logging
from uuid import uuid4
from typing import Optional

from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel

from app.services.runway_gen2 import generate_video_from_text
from app.config import settings  # agora usa TMP_DIR daqui

# === ⚙️ Logger ===
logger = logging.getLogger(__name__)

# === 🚀 Router ===
router = APIRouter(prefix="/ai", tags=["Runway Gen-2"])

# === 📦 Resposta ===
class RunwayResponse(BaseModel):
    status: str
    message: str
    filename: str  # retorna apenas o nome do arquivo gerado

# === 🎬 Endpoint: Geração de Vídeo com IA (sem S3) ===

@router.post("/generate-video", response_model=RunwayResponse)
async def generate_runway_video(
    prompt: str = Form(..., min_length=5, description="Texto descritivo para geração do vídeo"),
    duration: Optional[float] = Form(4.0, ge=1.0, le=10.0, description="Duração do vídeo em segundos"),
    seed: Optional[int] = Form(None, description="Semente opcional para reprodução do resultado")
):
    """
    Gera um vídeo com IA (Runway Gen-2) e salva localmente no diretório temporário.
    """
    filename = f"runway_{uuid4()}.mp4"
    output_path = os.path.join(settings.TMP_DIR, filename)

    try:
        logger.info(f"📥 Prompt recebido: {prompt[:60]}... | Duração: {duration}s")
        generate_video_from_text(prompt=prompt, output_path=output_path, duration=duration, seed=seed)

        logger.info(f"✅ Vídeo gerado com sucesso em: {output_path}")
        return RunwayResponse(
            status="success",
            message="Vídeo gerado com sucesso.",
            filename=filename  # frontend pode acessar via /media/{filename}
        )

    except Exception as e:
        logger.exception(f"❌ Erro ao gerar vídeo com IA: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar o vídeo com IA.")
