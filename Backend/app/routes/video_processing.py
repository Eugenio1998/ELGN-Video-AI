from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os, shutil, time, json, redis, logging
from datetime import datetime
from moviepy.editor import VideoFileClip
from celery.result import AsyncResult

from app.auth.dependencies import get_current_user
from app.services.video_processing_queue import process_video_high_priority, process_video_low_priority
from app.services.usage_limits import check_and_update_usage

router = APIRouter(tags=["Processamento"])

# === 📁 Diretórios ===
UPLOAD_DIR = "uploads/"
PROCESSED_DIR = "processed_videos/"
FAILED_DIR = "failed_videos/"
LOG_DIR = "logs/"
PROCESS_LOG = os.path.join(LOG_DIR, "process_times.json")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "failed_processing.log")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(FAILED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# === 🔌 Redis e Logger ===
redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "video_processing.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("video_processing")

# === ⬆️ Upload de vídeo com verificação ===
@router.post("/upload/video/")
def upload_video(
    user_id: str,
    plan: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """📤 Upload de vídeo com verificação de plano."""
    try:
        if not check_and_update_usage(user_id, plan):
            logger.warning(f"🚫 Limite atingido: {user_id} | Plano: {plan}")
            raise HTTPException(status_code=429, detail="Limite diário de processamento atingido.")

        filename = file.filename
        input_path = os.path.join(UPLOAD_DIR, filename)
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"📥 Vídeo '{filename}' recebido de {user_id}.")

        output_path = os.path.join(PROCESSED_DIR, f"processed_{filename}")
        task = process_video_high_priority if plan == "premium" else process_video_low_priority
        task_result = task.apply_async(args=[input_path, output_path])

        logger.info(f"🚀 Task Celery iniciada: {filename} | ID: {task_result.id}")
        return {"message": "Processamento iniciado", "task_id": task_result.id, "output_path": output_path}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"❌ Erro no processamento de vídeo")
        raise HTTPException(status_code=500, detail="Erro ao iniciar o processamento do vídeo.")

# === 🧪 Simulação de processamento ===
@router.post("/process-video-simulate")
def simulate_video_processing(video_name: str):
    """🧪 Simula o processamento de vídeo."""
    start = time.time()
    time.sleep(2)
    elapsed = time.time() - start
    logger.info(f"🧪 Simulação '{video_name}' | Tempo: {elapsed:.2f}s")

    try:
        process_times = []
        if os.path.exists(PROCESS_LOG):
            with open(PROCESS_LOG, "r") as f:
                process_times = json.load(f)
        process_times.append(elapsed)
        with open(PROCESS_LOG, "w") as f:
            json.dump(process_times, f)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar tempo simulado: {e}")

    return {"message": "Vídeo processado (simulado)", "process_time": round(elapsed, 2)}

# === ♻️ Reprocessar vídeos falhos ===
@router.post("/reprocess-failed-videos")
def reprocess_failed(current_user=Depends(get_current_user)):
    """♻️ Reprocessa vídeos que falharam anteriormente."""
    try:
        failed_files = os.listdir(FAILED_DIR)
        if not failed_files:
            logger.info(f"✅ Nenhum vídeo com falha (usuario: {current_user.username})")
            return {"message": "Nenhum vídeo com falha encontrado."}

        reprocessed = []
        for file in failed_files:
            input_path = os.path.join(FAILED_DIR, file)
            output_path = os.path.join(PROCESSED_DIR, f"processed_{file}")
            task = process_video_low_priority.apply_async(args=[input_path, output_path])
            reprocessed.append({"file": file, "task_id": task.id})
            logger.info(f"🔁 Reprocessando: {file} | ID: {task.id}")

        return {"message": "Reprocessamento iniciado", "reprocessed": reprocessed}
    except Exception as e:
        logger.exception("❌ Erro ao reprocessar vídeos")
        raise HTTPException(status_code=500, detail="Erro ao reprocessar vídeos.")

# === 📊 Status da fila ===
@router.get("/video/queue-status")
def get_queue_status():
    """📊 Consulta o tamanho da fila de vídeos (Redis)."""
    try:
        count = redis_conn.llen("video_queue")
        logger.info(f"📊 Fila consultada: {count} pendentes")
        return {"jobs_pendentes": count}
    except Exception as e:
        logger.exception("❌ Erro ao consultar fila Redis")
        raise HTTPException(status_code=500, detail="Erro ao consultar fila.")

# === ❌ Lista de vídeos com falha ===
@router.get("/failed-videos")
def get_failed_videos():
    """🚨 Lista vídeos com falha e exibe os últimos logs."""
    try:
        logs = []
        if os.path.exists(ERROR_LOG_FILE):
            with open(ERROR_LOG_FILE, "r") as error_log:
                logs = error_log.readlines()[-50:]
        failed_videos = os.listdir(FAILED_DIR)
        logger.info(f"📛 Falhas encontradas: {len(failed_videos)}")
        return {"failed_videos": failed_videos, "failed_logs": logs}
    except Exception as e:
        logger.exception("❌ Erro ao listar vídeos com falha")
        raise HTTPException(status_code=500, detail="Erro ao listar vídeos com falha.")
