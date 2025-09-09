# 📁 backend/app/api/endpoints/filters.py

import os
import logging
from typing import Optional, Literal

from fastapi import APIRouter, HTTPException, Form, Path
from pydantic import BaseModel
from app.config import settings
from app.tasks import apply_video_filter_task as apply_video_filter
from app.api.error_response import ErrorResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# === 📦 Schemas ===

class FilterTaskResponse(BaseModel):
    task_id: str
    message: str

# === 🎨 Endpoint: Aplicar Filtro Visual com IA ===

@router.post(
    "/filters/{video_id}/",
    response_model=FilterTaskResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Filtros"]
)
async def apply_filters(
    video_id: str = Path(..., description="ID ou nome do arquivo do vídeo"),
    filter_type: Literal["blur", "grayscale", "sepia", "vintage", "bw"] = Form(..., description="Tipo de filtro visual"),
    strength: Optional[float] = Form(None, ge=0.0, le=1.0, description="Intensidade do filtro (0.0 a 1.0)"),
    radius: Optional[int] = Form(None, ge=1, le=50, description="Raio para filtros de blur"),
    color: Optional[str] = Form(None, description="Cor em HEX ou nome para filtros de cor")
):
    """
    Inicia uma task assíncrona para aplicar um filtro visual a um vídeo.
    """
    try:
        video_path = os.path.join(settings.UPLOAD_FOLDER, video_id)

        if not os.path.exists(video_path):
            logger.warning(f"[{video_id}] Vídeo não encontrado em: {video_path}")
            raise HTTPException(status_code=404, detail="Vídeo não encontrado.")

        # ⛏️ Filtra apenas parâmetros relevantes
        filter_params = {
            "strength": strength,
            "radius": radius if filter_type == "blur" else None,
            "color": color if filter_type in ["sepia", "vintage"] else None
        }
        filter_params = {k: v for k, v in filter_params.items() if v is not None}

        task = apply_video_filter.delay(video_id, filter_type, filter_params)

        logger.info(f"[{video_id}] Filtro '{filter_type}' iniciado | Parâmetros: {filter_params} | Task ID: {task.id}")

        return FilterTaskResponse(
            task_id=task.id,
            message=f"Filtro '{filter_type}' iniciado com sucesso."
        )

    except Exception as e:
        logger.exception(f"[{video_id}] Erro ao aplicar filtro '{filter_type}': {e}")
        raise HTTPException(status_code=500, detail="Erro ao aplicar o filtro.")
