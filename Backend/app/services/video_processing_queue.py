# 📁 backend/app/services/video_tasks.py

import os
import ffmpeg
import logging
import multiprocessing
from uuid import uuid4
from datetime import datetime
from celery import Celery
from celery.result import AsyncResult
from prometheus_client import Gauge, start_http_server
from app.services.video_filters import split_video_by_scene
from dotenv import load_dotenv

load_dotenv()

# === ⚙️ Configurações Celery e Prometheus ===
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 8001))
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "processed")
LOG_FILE = os.path.join(os.getenv("LOG_DIR", "logs"), "video_processing_history.log")
ALERT_THRESHOLD = int(os.getenv("ALERT_THRESHOLD", 10))

os.makedirs(PROCESSED_DIR, exist_ok=True)

celery_app = Celery("video_tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery_app.conf.task_routes = {
    'app.services.video_tasks.process_video_high_priority': {'queue': 'high_priority'},
    'app.services.video_tasks.process_video_low_priority': {'queue': 'low_priority'},
    'app.services.video_tasks.process_scene_split_video': {'queue': 'split_queue'}
}

start_http_server(PROMETHEUS_PORT)

# === 📊 Métricas Prometheus ===
active_tasks_gauge = Gauge("video_processing_active_tasks", "Tarefas ativas")
scheduled_tasks_gauge = Gauge("video_processing_scheduled_tasks", "Tarefas agendadas")
reserved_tasks_gauge = Gauge("video_processing_reserved_tasks", "Tarefas reservadas")

# === 📝 Logger ===
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def log_history(message: str):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

# === 🎬 Tasks ===
@celery_app.task(bind=True, max_retries=2, countdown=10)
def process_scene_split_video(self, video_path: str, user_id: str = "default"):
    logger.info(f"🎞️ Corte por cenas para {video_path}")
    try:
        output_dir = os.path.join(PROCESSED_DIR, f"user_{user_id}", f"scenes_{uuid4()}")
        os.makedirs(output_dir, exist_ok=True)
        segments = split_video_by_scene(video_path, output_dir)
        return {"status": "success", "segments": segments}
    except Exception as e:
        logger.error(f"❌ Erro corte por cenas: {e}")
        raise self.retry(exc=e)

@celery_app.task(bind=True, max_retries=3, countdown=5)
def process_video_high_priority(self, video_path: str, output_path: str):
    return _run_ffmpeg_process(self, video_path, output_path, "alta prioridade")

@celery_app.task(bind=True, max_retries=2, countdown=10)
def process_video_low_priority(self, video_path: str, output_path: str):
    return _run_ffmpeg_process(self, video_path, output_path, "baixa prioridade")

def _run_ffmpeg_process(self, video_path: str, output_path: str, level: str):
    try:
        logger.info(f"🎯 {level.title()}: {video_path} → {output_path}")
        ffmpeg.input(video_path).output(output_path, format='mp4', vcodec='libx264', preset='slow').run(overwrite_output=True)
        log_history(f"{level.title()} concluída: {output_path}")
        return {"status": "success", "output": output_path}
    except ffmpeg.Error as e:
        stderr = e.stderr.decode() if hasattr(e, "stderr") else str(e)
        logger.error(f"FFmpeg Error: {stderr}")
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise self.retry(exc=e)

# === 🧠 Ajuste de Workers (Opcional) ===
def adjust_worker_allocation():
    try:
        stats = celery_app.control.stats()
        if stats:
            total_active = sum(worker.get('active', 0) for worker in stats.values())
            cpu_cores = multiprocessing.cpu_count()
            new_workers = min(max(1, total_active // 2 + 1), cpu_cores * 2)
            os.system(f'celery -A backend.app.services.video_tasks worker --autoscale={new_workers},{cpu_cores * 2} --detach -Ofair')
            log_history(f"Alocação ajustada: {new_workers} workers.")
    except Exception as e:
        logger.error(f"Erro ao ajustar workers: {e}")
