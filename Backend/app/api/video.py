import os
import logging
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, constr

from app.services.processing_pipeline import full_video_pipeline
from app.services.usage_limits import check_and_update_usage
from app.services.audit_logging import log_video_upload
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.api.error_response import ErrorResponse
from app.config import settings

router = APIRouter(prefix="/video", tags=["Video"])
logger = logging.getLogger(__name__)

# === 📦 SCHEMA (Form para uso com UploadFile) ===

class VideoProcessInput(BaseModel):
    apply_cutting: bool = Form(True)
    filter_type: Optional[constr(max_length=50)] = Form(None)
    filter_source: Optional[constr(max_length=50)] = Form("opencv")
    style_model_path: Optional[constr(max_length=255)] = Form(None)
    transcribe: bool = Form(False)
    transcription_format: constr(max_length=10) = Form("json")
    generate_voice_ia: bool = Form(False)
    voice_text: Optional[str] = Form(None)
    voice_lang: constr(max_length=10) = Form("pt")
    voice_provider: constr(max_length=50) = Form("gtts")
    separar_cenas: bool = Form(False)

# === 🎥 PROCESSAMENTO PRINCIPAL ===

@router.post(
    "/process",
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
def process_video_route(
    file: UploadFile = File(...),
    form: VideoProcessInput = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    local_input = None

    try:
        # Verifica tipo MIME
        if not file.content_type or not file.content_type.startswith("video/"):
            logger.warning(f"❌ Arquivo inválido enviado por {current_user.username}")
            raise HTTPException(status_code=400, detail="Por favor, envie um arquivo de vídeo.")

        # Checa e atualiza limite de uso
        if not check_and_update_usage(current_user.id, plan="premium"):
            raise HTTPException(status_code=429, detail="Limite diário de uso atingido.")

        # Cria diretório temporário
        temp_dir = os.path.join(settings.TMP_DIR, "video_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        local_input = os.path.join(temp_dir, file.filename)

        # Salva arquivo temporário
        with open(local_input, "wb") as f:
            while chunk := file.file.read(1024 * 1024):
                f.write(chunk)

        logger.info(f"📥 Vídeo recebido de {current_user.username} ({file.filename})")

        # Executa pipeline principal
        result = full_video_pipeline(
            input_path=local_input,
            apply_cutting=form.apply_cutting,
            filter_type=form.filter_type,
            filter_source=form.filter_source,
            style_model_path=form.style_model_path,
            transcribe=form.transcribe,
            transcription_format=form.transcription_format,
            generate_voice_ia=form.generate_voice_ia,
            voice_text=form.voice_text,
            voice_lang=form.voice_lang,
            voice_provider=form.voice_provider,
            separar_cenas=form.separar_cenas
        )

        # Log de uso
        log_video_upload(current_user.id, db)

        logger.info(f"✅ Processamento concluído para {current_user.username}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao processar vídeo de {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar o vídeo.")
    finally:
        if local_input and os.path.exists(local_input):
            os.remove(local_input)
            logger.debug(f"🧹 Arquivo temporário removido: {local_input}")
