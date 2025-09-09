# 📁 backend/app/schemas/video.py

from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional, List, Annotated


class VideoCreate(BaseModel):
    """Modelo de entrada para envio de vídeo."""
    original_filename: Annotated[
        str,
        Field(..., description="Nome do arquivo enviado", example="meuvideo.mp4")
    ]


class VideoOut(BaseModel):
    """Resposta com os dados de um vídeo processado."""

    id: Annotated[int, Field(description="ID único do vídeo", example=42)]
    user_id: Annotated[int, Field(description="ID do usuário dono do vídeo", example=1)]
    processed_url: Annotated[
        HttpUrl,
        Field(description="URL do vídeo processado", example="https://cdn.elgn.ai/videos/abc123.mp4")
    ]
    created_at: Annotated[
        datetime,
        Field(description="Data/hora de envio do vídeo", example="2025-05-27T14:00:00Z")
    ]
    original_filename: Annotated[
        Optional[str],
        Field(None, description="Nome original do arquivo", example="meuvideo.mp4")
    ]
    duration: Annotated[
        Optional[float],
        Field(None, description="Duração do vídeo em segundos", example=125.3)
    ]
    size_bytes: Annotated[
        Optional[int],
        Field(None, description="Tamanho do vídeo em bytes", example=10500000)
    ]
    format: Annotated[
        Optional[str],
        Field(None, description="Formato do vídeo", example="mp4")
    ]
    status: Annotated[
        Optional[str],
        Field(None, description="Status do processamento", example="completed")
    ]

    model_config = {
        "from_attributes": True
    }


VideoListOut = List[VideoOut]

class VideoProcessedResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    status: str
    size: int = Field(..., description="Tamanho do vídeo em bytes")