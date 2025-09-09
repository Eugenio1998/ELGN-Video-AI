from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4
import os
import shutil
import logging

from moviepy.editor import VideoFileClip

from app.services.processing_pipeline import full_video_pipeline
from app.models.video import Video
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["Upload"])

# === 📁 Diretórios e formatos ===
UPLOAD_DIR = "uploads/"
PROCESSED_DIR = "processed_videos/"
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

logger = logging.getLogger("upload_local")

# === 🔎 Validação de extensão ===
def is_allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

# === 🆔 Geração de nome único ===
def generate_unique_filename(filename: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name, ext = os.path.splitext(filename)
    return f"{name}_{timestamp}{ext}"

# === ⬆️ Upload e processamento do vídeo ===
@router.post("/upload")
def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_allowed_file(file.filename):
        logger.warning(f"❌ Formato inválido: {file.filename} por {current_user.username}")
        raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

    unique_filename = generate_unique_filename(file.filename)
    upload_path = os.path.join(UPLOAD_DIR, unique_filename)
    processed_path = os.path.join(PROCESSED_DIR, unique_filename)

    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"📥 Upload salvo: '{unique_filename}' por {current_user.username}")
    except Exception as e:
        logger.exception(f"❌ Erro ao salvar vídeo '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar vídeo.")

    try:
        # 🧠 Executar processamento com IA
        logger.info(f"🧠 Início do processamento IA: '{unique_filename}' por {current_user.username}")
        full_video_pipeline(input_path=upload_path)

        # 📦 Mover vídeo processado
        shutil.move(upload_path, processed_path)

        # ⏱️ Duração do vídeo
        clip = VideoFileClip(processed_path)
        duration = round(clip.duration, 2)
        clip.close()

        # 💾 Registro no banco de dados
        video = Video(
            filename=unique_filename,
            user_id=current_user.id,
            uploaded_at=datetime.utcnow(),
            duration=duration
        )
        db.add(video)
        db.commit()
        logger.info(f"✅ Processamento finalizado: '{unique_filename}' ({duration}s) por {current_user.username}")

        return {
            "message": "🎬 Vídeo enviado e processado com sucesso!",
            "filename": unique_filename,
            "duration": duration,
            "uploaded_at": video.uploaded_at.isoformat()
        }

    except Exception as e:
        logger.exception(f"❌ Erro no processamento do vídeo '{unique_filename}': {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar vídeo.")

# === 📂 Listar vídeos processados ===
@router.get("/videos", dependencies=[Depends(get_current_user)])
def list_videos():
    try:
        files = [
            f for f in os.listdir(PROCESSED_DIR)
            if not f.startswith(".") and os.path.isfile(os.path.join(PROCESSED_DIR, f))
        ]
        return {
            "count": len(files),
            "processed_videos": files
        }
    except Exception as e:
        logger.exception(f"❌ Erro ao listar vídeos processados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar vídeos.")
