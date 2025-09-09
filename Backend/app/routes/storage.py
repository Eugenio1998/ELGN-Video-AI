# 📁 app/routes/storage.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.audio import Audio
from app.models.image import Image

router = APIRouter()

@router.get("/storage")
async def get_storage(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retorna o uso de armazenamento (em bytes) por tipo de arquivo do usuário atual.
    
    Os limites são baseados no plano:
    - Free / Basic: 0 bytes
    - Pro: 100 GB
    - Premium: 500 GB
    - Empresarial: 1 TB
    """
    # Bytes utilizados
    total_bytes = 0

    video_size = db.query(Video).filter(Video.user_id == current_user.id).with_entities(Video.size).all()
    audio_size = db.query(Audio).filter(Audio.user_id == current_user.id).with_entities(Audio.size).all()
    image_size = db.query(Image).filter(Image.user_id == current_user.id).with_entities(Image.size).all()

    total_bytes += sum([v[0] for v in video_size if v[0]])
    total_bytes += sum([a[0] for a in audio_size if a[0]])
    total_bytes += sum([i[0] for i in image_size if i[0]])

    # Limite do plano
    plan_name = current_user.plan.name.lower() if current_user.plan else "free"
    limits = {
        "free": 0,
        "basic": 0,
        "pro": 100 * 1024**3,         # 100 GB
        "pro anual": 200 * 1024**3,    # 200 GB
        "premium": 500 * 1024**3,     # 500 GB
        "premium anual": 1000 * 1024**3,
        "empresarial": 1024 * 1024**3,
        "empresarial anual": 2048 * 1024**3
    }
    max_bytes = limits.get(plan_name, 0)

    return {
        "plan": plan_name,
        "used": total_bytes,
        "limit": max_bytes,
        "percentage": round((total_bytes / max_bytes) * 100, 2) if max_bytes else 0.0
    }
