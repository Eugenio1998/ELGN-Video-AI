import os
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from api.deps import get_current_user, require_role
from app.models.user import User, UserRole

# === 🔧 Configurações iniciais ===
router = APIRouter()
PROCESSED_DIR = os.getenv("PROCESSED_VIDEOS_DIR", "processed_videos")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# === 📝 Logger ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === 📦 Modelo da requisição ===
class DeleteVideoRequest(BaseModel):
    video_name: str

# === 🧹 Função de exclusão de vídeo ===
def delete_video_file(video_name: str) -> None:
    video_path = os.path.join(PROCESSED_DIR, video_name)

    if not os.path.exists(video_path):
        logging.warning(f"⚠️ Arquivo não encontrado para exclusão: {video_path}")
        return

    try:
        os.remove(video_path)
        logging.info(f"🗑️ Vídeo excluído com sucesso: {video_path}")
    except Exception as e:
        logging.error(f"❌ Erro ao excluir vídeo {video_name}: {e}")

# === 📡 Endpoint: Excluir vídeo processado ===
@router.post("/delete-video", tags=["Admin"], dependencies=[Depends(require_role(UserRole.ADMIN))])
def delete_video(
    request: DeleteVideoRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    🧹 Inicia a exclusão assíncrona de um vídeo processado.
    🔒 Disponível apenas para administradores.
    """
    background_tasks.add_task(delete_video_file, request.video_name)
    return {
        "message": f"🕓 Exclusão iniciada para: {request.video_name}",
        "requested_by": current_user.username,
        "timestamp": datetime.utcnow().isoformat()
    }
