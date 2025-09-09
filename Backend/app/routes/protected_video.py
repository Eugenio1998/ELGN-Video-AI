import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.video import Video
from app.models.user import User, UserRole
from app.schemas.videos import VideoOut

router = APIRouter(tags=["Vídeos"])
logger = logging.getLogger(__name__)

@router.get("/videos/", response_model=dict)
def list_videos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    📼 Lista vídeos processados:
    - 👑 Admins veem todos os vídeos.
    - 👤 Usuários veem apenas seus próprios.
    """
    try:
        if current_user.role == UserRole.ADMIN:
            videos: List[Video] = db.query(Video).all()
        else:
            videos: List[Video] = (
                db.query(Video)
                .filter(Video.user_id == current_user.id)
                .all()
            )

        return {
            "user": current_user.username,
            "role": current_user.role.value,
            "total": len(videos),
            "videos": [VideoOut.from_orm(v) for v in videos],
        }

    except Exception as e:
        logger.error(f"❌ Erro ao buscar vídeos - Usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar vídeos.")
