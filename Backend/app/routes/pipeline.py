import os
import logging
from uuid import uuid4
from typing import Optional

from fastapi import (
    APIRouter, UploadFile, File, Form, HTTPException, Depends
)
from fastapi.responses import JSONResponse

from services.processing_pipeline import full_video_pipeline
from api.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["Pipeline"])
logger = logging.getLogger(__name__)


@router.post("/process-full/", tags=["Pipeline"], dependencies=[Depends(get_current_user)])
async def process_full_video(
    file: UploadFile = File(...),
    apply_cutting: bool = Form(default=True),
    filter_type: Optional[str] = Form(default=None),
    filter_source: str = Form(default="opencv"),
    style_model_path: Optional[str] = Form(default=None),
    transcribe: bool = Form(default=False),
    transcription_format: str = Form(default="json"),
    generate_voice_ia: bool = Form(default=False),
    voice_text: Optional[str] = Form(default=None),
    voice_lang: str = Form(default="pt"),
    voice_provider: str = Form(default="gtts"),
    separar_cenas: bool = Form(default=False),
    current_user: User = Depends(get_current_user)
):
    """
    🔁 Executa todo o pipeline inteligente de vídeo com filtros, corte, transcrição e narração por IA.
    """

    # 🚫 Validação de tipo
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é um vídeo válido.")

    # 📦 Limite de tamanho opcional (200MB)
    if hasattr(file, "spool_max_size") and file.spool_max_size and file.spool_max_size > 200_000_000:
        raise HTTPException(status_code=413, detail="O vídeo excede o tamanho permitido.")

    # 🗂️ Caminho de armazenamento temporário
    ext = file.filename.split(".")[-1]
    input_path = os.path.join("/tmp", f"{uuid4()}.{ext}")

    try:
        # 💾 Gravação do vídeo temporário
        with open(input_path, "wb") as f:
            while chunk := await file.read(8192):
                f.write(chunk)

        # 🧠 Execução do pipeline inteligente
        result = full_video_pipeline(
            input_path=input_path,
            apply_cutting=apply_cutting,
            filter_type=filter_type,
            filter_source=filter_source,
            style_model_path=style_model_path,
            transcribe=transcribe,
            transcription_format=transcription_format,
            generate_voice_ia=generate_voice_ia,
            voice_text=voice_text,
            voice_lang=voice_lang,
            voice_provider=voice_provider,
            separar_cenas=separar_cenas,
            user_id=current_user.id
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": "processing started",
                "result": result
            }
        )

    except Exception as e:
        logger.error(f"❌ Erro no pipeline - Usuário {current_user.id} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar vídeo: {str(e)}")

    finally:
        # 🧹 Remoção do arquivo temporário
        if os.path.exists(input_path):
            os.remove(input_path)
