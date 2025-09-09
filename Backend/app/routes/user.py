from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
import os, redis, logging
from rq import Queue

from app.middleware import verify_permission
from app.database import get_db
from app.models.user import User
from app.models.video import Video

router = APIRouter(tags=["Admin"])
logger = logging.getLogger("user_admin")

# === 🔗 Redis e Fila RQ ===
redis_conn = redis.Redis(host="localhost", port=6379, db=0)
queue = Queue("video_processing", connection=redis_conn)

# === 📦 Schemas ===
class UserSchema(BaseModel):
    email: EmailStr
    role: str  # admin | user

# === 👥 Gerenciamento de Usuários ===

@router.get("/admin/users")
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(lambda: verify_permission(required_role="admin"))
):
    """🔍 Lista todos os usuários (Admin)."""
    try:
        users = db.query(User).all()
        return [{"id": u.id, "email": u.email, "role": u.role} for u in users]
    except Exception as e:
        logger.exception("❌ Erro ao listar usuários")
        raise HTTPException(status_code=500, detail="Erro ao listar usuários")

@router.post("/admin/users")
def add_user(
    new_user: UserSchema,
    db: Session = Depends(get_db),
    current_user=Depends(lambda: verify_permission(required_role="admin"))
):
    """➕ Adiciona um novo usuário (Admin)."""
    try:
        if db.query(User).filter(User.email == new_user.email).first():
            raise HTTPException(status_code=400, detail="E-mail já registrado.")

        user_entry = User(email=new_user.email, role=new_user.role)
        db.add(user_entry)
        db.commit()
        db.refresh(user_entry)
        logger.info(f"🟢 Novo usuário adicionado: {user_entry.email}")
        return {"message": "Usuário adicionado com sucesso", "user_id": user_entry.id}

    except Exception as e:
        logger.exception("❌ Erro ao adicionar usuário")
        raise HTTPException(status_code=500, detail="Erro ao adicionar usuário")

@router.put("/admin/users/{user_id}")
def update_user_role(
    user_id: int,
    updated_user: UserSchema,
    db: Session = Depends(get_db),
    current_user=Depends(lambda: verify_permission(required_role="admin"))
):
    """🔄 Atualiza a role de um usuário (Admin)."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        user.role = updated_user.role
        db.commit()
        logger.info(f"🔁 Role atualizada: {user.email} → {user.role}")
        return {"message": "Função do usuário atualizada"}
    except Exception as e:
        logger.exception("❌ Erro ao atualizar função")
        raise HTTPException(status_code=500, detail="Erro ao atualizar função")

@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(lambda: verify_permission(required_role="admin"))
):
    """🗑️ Remove um usuário (Admin)."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        db.delete(user)
        db.commit()
        logger.info(f"🗑️ Usuário removido: {user.email}")
        return {"message": "Usuário removido com sucesso"}
    except Exception as e:
        logger.exception("❌ Erro ao remover usuário")
        raise HTTPException(status_code=500, detail="Erro ao remover usuário")

# === 🧠 Fila RQ: status e logs ===

@router.get("/admin/queue/status")
def queue_status_panel(
    current_user=Depends(lambda: verify_permission(required_role="admin"))
):
    """📊 Painel com status da fila de processamento (Admin)."""
    try:
        return {
            "pendentes": len(queue.job_ids),
            "em_execucao": len(queue.started_job_registry.get_job_ids()),
            "concluidos": len(queue.finished_job_registry.get_job_ids()),
            "falhos": len(queue.failed_job_registry.get_job_ids())
        }
    except Exception as e:
        logger.exception("❌ Erro ao obter status da fila")
        raise HTTPException(status_code=500, detail="Erro ao obter status da fila")

@router.get("/admin/queue/logs")
def queue_logs(
    current_user=Depends(lambda: verify_permission(required_role="admin"))
):
    """🧾 Exibe os últimos logs de processamento de vídeos (Admin)."""
    log_path = "logs/video_processing.log"
    try:
        if not os.path.exists(log_path):
            return {"logs": []}
        with open(log_path, "r", encoding="utf-8") as f:
            return {"logs": f.readlines()[-50:]}
    except Exception as e:
        logger.exception("❌ Erro ao ler logs da fila")
        raise HTTPException(status_code=500, detail="Erro ao ler logs")

# === 🎞 Registro manual de vídeos ===

@router.post("/admin/video/register")
def register_video_metadata(
    filename: str,
    duration: float,
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(lambda: verify_permission(required_role="admin"))
):
    """📝 Registra metadados manuais de vídeo (Admin)."""
    try:
        video = Video(
            filename=filename,
            duration=duration,
            uploaded_by=user_id,
            created_at=datetime.utcnow()
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        logger.info(f"📝 Metadados salvos para vídeo: {filename}")
        return {"message": "Metadados do vídeo salvos com sucesso.", "video_id": video.id}
    except Exception as e:
        logger.exception("❌ Erro ao registrar metadados do vídeo")
        raise HTTPException(status_code=500, detail="Erro ao registrar metadados do vídeo")
