from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import os, logging

from app.auth.dependencies import get_current_user
from app.services.video_processing_queue import process_video_low_priority

router = APIRouter(tags=["Vídeos"])

# === 📁 Diretórios ===
PROCESSED_DIR = "processed_videos/"
FAILED_DIR = "failed_videos/"

# === 🛠 Logger ===
logger = logging.getLogger("video_status")

# === 📊 Status de vídeos processados ou com falha ===
@router.get("/video-status")
def get_video_status(current_user=Depends(get_current_user)):
    """📊 Retorna lista de vídeos processados e falhos (usuário autenticado)."""
    try:
        processed_videos = [
            {
                "id": f,
                "name": f,
                "status": "completed",
                "file_path": os.path.join(PROCESSED_DIR, f)
            }
            for f in os.listdir(PROCESSED_DIR)
        ]
        failed_videos = [
            {
                "id": f,
                "name": f,
                "status": "failed",
                "file_path": os.path.join(FAILED_DIR, f)
            }
            for f in os.listdir(FAILED_DIR)
        ]
        logger.info(f"📊 Status consultado por {current_user.username} | OK: {len(processed_videos)} | Falha: {len(failed_videos)}")
        return {"videos": processed_videos + failed_videos}

    except FileNotFoundError:
        logger.error("❌ Diretórios de vídeo não encontrados.")
        raise HTTPException(status_code=500, detail="Erro ao acessar diretórios de vídeos.")
    except Exception as e:
        logger.error(f"❌ Erro ao obter status de vídeos ({current_user.username}): {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter status dos vídeos.")

# === ♻️ Reprocessamento manual de vídeo ===
@router.post("/reprocess-video")
def reprocess_video(video_id: str, current_user=Depends(get_current_user)):
    """♻️ Reenvia vídeo falho para fila de processamento."""
    failed_path = os.path.join(FAILED_DIR, video_id)
    output_path = os.path.join(PROCESSED_DIR, f"processed_{video_id}")

    if not os.path.exists(failed_path):
        logger.warning(f"⚠️ Arquivo não encontrado para reprocessar: {video_id} | Usuário: {current_user.username}")
        raise HTTPException(status_code=404, detail="Vídeo não encontrado para reprocessamento.")

    try:
        task = process_video_low_priority.apply_async(args=[failed_path, output_path])
        logger.info(f"♻️ Reprocessamento: {video_id} | Task ID: {task.id} | Usuário: {current_user.username}")
        return {"message": "Reprocessamento iniciado com sucesso!", "task_id": task.id}
    except Exception as e:
        logger.error(f"❌ Erro ao reprocessar '{video_id}': {e}")
        raise HTTPException(status_code=500, detail="Erro ao reprocessar vídeo.")

# === ⬇️ Download do vídeo processado ===
@router.get("/download/{file_path:path}")
def download_video(file_path: str, current_user=Depends(get_current_user)):
    """⬇️ Permite baixar vídeo processado autenticado."""
    full_path = os.path.join(PROCESSED_DIR, file_path)

    if not os.path.exists(full_path):
        logger.warning(f"⚠️ Arquivo para download não encontrado: {file_path} | Usuário: {current_user.username}")
        raise HTTPException(status_code=404, detail="Arquivo não encontrado para download.")

    logger.info(f"⬇️ Download: {file_path} | Usuário: {current_user.username}")
    return FileResponse(path=full_path, filename=file_path, media_type="video/mp4")
