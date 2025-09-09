# 📁 app/routes/video_routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.video import Video
from app.auth.dependencies import get_current_user
from app.models.user import User

from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v1/videos",
    tags=["Vídeos"]
)

# 📦 Resposta para vídeos processados
class VideoProcessedResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    status: str
    size: int = Field(..., description="Tamanho do vídeo em bytes")

    model_config = {
        "from_attributes": True
    }

@router.get("/processed", response_model=List[VideoProcessedResponse])
def list_processed_videos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna todos os vídeos processados do usuário logado.
    """
    videos = (
        db.query(Video)
        .filter(Video.user_id == current_user.id)
        .filter(Video.status == "processed")
        .order_by(Video.created_at.desc())
        .all()
    )

    return [
        VideoProcessedResponse(
            id=str(video.id),
            title=video.original_filename or "Vídeo sem nome",
            created_at=video.created_at,
            status=video.status or "unknown",
            size=video.size or 0
        )
        for video in videos
    ]
