import logging
import os
from celery import Celery
from dotenv import load_dotenv

# === 📦 Carregar variáveis de ambiente ===
load_dotenv()

# === 🔗 Configuração do Celery ===
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery = Celery("elgn_ai_tasks", broker=REDIS_URL)

# === 🛠️ Logger ===
logger = logging.getLogger("queue_status")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === ⏳ Obter tarefas Celery pendentes, ativas e agendadas ===
def list_pending_tasks() -> dict:
    """🔍 Lista tarefas pendentes, ativas e agendadas dos workers Celery."""
    inspector = celery.control.inspect()
    if not inspector:
        logger.warning("📡 Nenhum worker Celery conectado.")
        return {}

    return {
        "active": inspector.active() or {},
        "scheduled": inspector.scheduled() or {},
        "reserved": inspector.reserved() or {},
    }

# === 📊 Obter todos os estados de tarefas ===
def get_all_task_states() -> dict:
    """📊 Lista todos os estados conhecidos das tarefas no cluster Celery."""
    inspector = celery.control.inspect()
    if not inspector:
        logger.warning("📡 Nenhum worker Celery conectado.")
        return {}

    return {
        "active": inspector.active() or {},
        "scheduled": inspector.scheduled() or {},
        "reserved": inspector.reserved() or {},
        "failed": inspector.failed() or {},
        "revoked": inspector.revoked() or {},
    }

# === ♻️ Reiniciar tarefas com falha ===
def restart_failed_tasks() -> dict:
    """♻️ Reenvia tarefas com status 'failed'."""
    inspector = celery.control.inspect()
    if not inspector:
        logger.warning("📡 Nenhum worker Celery conectado.")
        return {"message": "Nenhum worker Celery disponível."}

    failed_tasks = inspector.failed() or {}
    reiniciadas = []

    for worker, tasks in failed_tasks.items():
        for task in tasks:
            task_id = task.get("id")
            task_name = task.get("name")
            args = task.get("args", [])
            kwargs = task.get("kwargs", {})

            if task_id and task_name:
                try:
                    celery.send_task(task_name, args=args, kwargs=kwargs)
                    reiniciadas.append(task_id)
                    logger.warning(f"🔁 Tarefa {task_id} ({task_name}) reiniciada com sucesso.")
                except Exception as e:
                    logger.error(f"❌ Erro ao reenviar tarefa {task_id}: {e}")

    return {
        "restarted_tasks": reiniciadas,
        "message": f"{len(reiniciadas)} tarefas reenviadas.",
    }
