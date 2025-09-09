# 🚀 Celery Worker e Agendador

import os
import logging
from celery import Celery
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import SessionLocal
from app.routes.push_cleanup import validate_and_clean_push_subscriptions

# === 🔧 Variáveis de Ambiente ===
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

if not CELERY_BROKER_URL:
    raise ValueError("❌ CELERY_BROKER_URL não configurado")

# === ⚙️ Instância Celery ===
celery = Celery("elgn_ai_tasks", broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)

# === 🛠 Logger ===
logger = logging.getLogger("elgn_worker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# === 🧾 Verificação de Assinaturas (Diária) ===
@celery.task(name="tasks.run_subscription_check", bind=True, max_retries=3)
def run_subscription_check(self):
    """🧾 Executa verificação de assinaturas com retries."""
    db: Session = SessionLocal()
    try:
        logger.info("🧾 Iniciando verificação automática de assinaturas...")
        check_subscription_status(db)
        logger.info("✅ Verificação de assinaturas concluída com sucesso.")
    except Exception as e:
        logger.error(f"❌ Erro na verificação de assinaturas: {e}")
        db.rollback()
        retry_num = self.request.retries + 1
        if retry_num <= self.max_retries:
            logger.warning(f"🔁 Tentativa {retry_num} de {self.max_retries}...")
            raise self.retry(exc=e, countdown=60)
        logger.critical("🛑 Máximo de tentativas atingido.")
    finally:
        db.close()

# === 🧹 Limpeza de Push Subscriptions (Diária) ===
@celery.task(name="tasks.cleanup_push_subscriptions", bind=True, max_retries=3)
def cleanup_push_subscriptions(self):
    """🧹 Limpa inscrições push expiradas com retries."""
    try:
        logger.info("🧹 Iniciando limpeza de inscrições push expiradas...")
        result = validate_and_clean_push_subscriptions()
        logger.info(f"✅ Limpeza finalizada: {result}")
    except Exception as e:
        logger.error(f"❌ Erro ao limpar inscrições push: {e}")
        retry_num = self.request.retries + 1
        if retry_num <= self.max_retries:
            logger.warning(f"🔁 Tentativa {retry_num} de {self.max_retries}...")
            raise self.retry(exc=e, countdown=3600)
        logger.critical("🛑 Máximo de tentativas atingido.")

# === ⏱️ Agendamento com Celery Beat ===
DAILY = 86400.0  # 24 horas

celery.conf.beat_schedule = {
    "check-subscriptions-daily": {
        "task": "tasks.run_subscription_check",
        "schedule": DAILY,
        "options": {"expires": DAILY + 3600},
    },
    "cleanup-push-subscriptions-daily": {
        "task": "tasks.cleanup_push_subscriptions",
        "schedule": DAILY,
        "options": {"expires": DAILY + 3600},
    },
}
celery.conf.timezone = "UTC"
