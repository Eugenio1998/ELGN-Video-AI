# 📁 app/celery_app.py

import os
import logging
from celery import Celery
from app.config import settings  # ⬅️ importa configurações centralizadas

# === 🛠️ Logger Setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)
logger = logging.getLogger(__name__)

# === ⚙️ Segurança para Docker (evita erro como root) ===
os.environ.setdefault("C_FORCE_ROOT", "true")

# === 📦 Variáveis obrigatórias do .env ===
BROKER_URL = settings.celery_broker_url
RESULT_BACKEND = settings.celery_result_backend

logger.info(f"🚀 Iniciando Celery com broker: {BROKER_URL} e backend: {RESULT_BACKEND}")

# === 🧠 Instância do Celery ===
celery_app = Celery(
    "elgn_ai",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=[
        "app.tasks",
        "app.services.video_processing_queue",
        # "app.services.analytics_queue",       # habilitar futuramente
        # "app.services.notifications_queue",   # habilitar futuramente
    ]
)

# === ⚙️ Configurações adicionais ===
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)

# === ✅ Mensagem final ===
logger.info("✅ Celery configurado com sucesso e pronto para processar tarefas.")
