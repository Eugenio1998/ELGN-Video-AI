from fastapi import APIRouter, HTTPException, Depends
from typing import List
import os
import shutil
import logging
import uuid

from app.auth.dependencies import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter(tags=["Admin"])

# === 📁 Diretórios da fila
QUEUE_DIR = "queued_videos/"
PROCESSING_DIR = "processing_videos/"
os.makedirs(QUEUE_DIR, exist_ok=True)
os.makedirs(PROCESSING_DIR, exist_ok=True)

# === 📋 Logger local
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === 🔍 Utilitário: Lista arquivos válidos
def _safe_list_files(directory: str) -> List[str]:
    return [
        f for f in os.listdir(directory)
        if not f.startswith('.') and "__MACOSX" not in f and os.path.isfile(os.path.join(directory, f))
    ]


# === 📥 Listar fila de vídeos
@router.get("/queue/", dependencies=[Depends(require_role(UserRole.ADMIN))])
def list_queue(current_user: User = Depends(get_current_user)):
    try:
        files = _safe_list_files(QUEUE_DIR)
        logger.info(f"📄 Fila consultada por {current_user.username}: {files}")
        return {"queue": files}
    except Exception as e:
        logger.exception("❌ Erro ao listar a fila")
        raise HTTPException(status_code=500, detail="Erro ao listar a fila.")


# === ⚡ Priorizar vídeo
@router.post("/queue/prioritize", dependencies=[Depends(require_role(UserRole.ADMIN))])
def prioritize_video(video_name: str, current_user: User = Depends(get_current_user)):
    file_path = os.path.join(QUEUE_DIR, video_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Vídeo não encontrado.")

    priority_prefix = f"{uuid.uuid4().hex[:8]}__PRIORITY__"
    prioritized_path = os.path.join(QUEUE_DIR, f"{priority_prefix}{video_name}")
    try:
        os.rename(file_path, prioritized_path)
        logger.info(f"⚡ Vídeo priorizado por {current_user.username}: {prioritized_path}")
        return {"message": f"{video_name} priorizado com sucesso."}
    except Exception as e:
        logger.exception("❌ Falha ao priorizar vídeo")
        raise HTTPException(status_code=500, detail=f"Erro ao priorizar vídeo: {e}")


# === 🗑️ Remover vídeo da fila
@router.delete("/queue/remove", dependencies=[Depends(require_role(UserRole.ADMIN))])
def remove_from_queue(video_name: str, current_user: User = Depends(get_current_user)):
    file_path = os.path.join(QUEUE_DIR, video_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    try:
        os.remove(file_path)
        logger.info(f"🗑️ Vídeo removido da fila por {current_user.username}: {video_name}")
        return {"message": f"{video_name} removido com sucesso."}
    except Exception as e:
        logger.exception("❌ Falha ao remover vídeo da fila")
        raise HTTPException(status_code=500, detail=f"Erro ao remover vídeo: {e}")


# === 🔁 Reorganizar ordem da fila
@router.post("/queue/reorder", dependencies=[Depends(require_role(UserRole.ADMIN))])
def reorder_queue(video_order: List[str], current_user: User = Depends(get_current_user)):
    current_files = set(_safe_list_files(QUEUE_DIR))

    if set(video_order) != current_files:
        raise HTTPException(status_code=400, detail="Lista de arquivos não corresponde à fila atual.")

    temp_dir = f"{QUEUE_DIR}_tmp"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Copia com prefixos ordenados
        for idx, filename in enumerate(video_order):
            src = os.path.join(QUEUE_DIR, filename)
            dst = os.path.join(temp_dir, f"{idx:03d}_{filename}")
            shutil.copy2(src, dst)

        # Remove originais e move reorganizados de volta
        for f in _safe_list_files(QUEUE_DIR):
            os.remove(os.path.join(QUEUE_DIR, f))

        for f in sorted(os.listdir(temp_dir)):
            src = os.path.join(temp_dir, f)
            original_name = f.split("_", 1)[1]
            dst = os.path.join(QUEUE_DIR, original_name)
            shutil.move(src, dst)

        shutil.rmtree(temp_dir)
        logger.info(f"🔄 Fila reorganizada por {current_user.username}")
        return {"message": "Fila reorganizada com sucesso."}

    except Exception as e:
        logger.exception("❌ Erro ao reorganizar a fila")
        raise HTTPException(status_code=500, detail=f"Erro ao reorganizar a fila: {e}")
