# 🧩 Monitoramento e Controle das Tarefas Celery

import os
import csv
import logging
from tempfile import NamedTemporaryFile
from celery import Celery
from celery.result import AsyncResult
from dotenv import load_dotenv

# === 🔐 Variáveis de Ambiente ===
load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# === 🚀 Inicialização do Celery ===
celery = Celery("elgn_ai_tasks", broker=REDIS_URL)

# === 🛠️ Logger ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(message)s")
logger = logging.getLogger("celery_monitor")

# === 🔎 Status de uma Tarefa ===
def get_task_status(task_id: str) -> dict:
    """Retorna o status de uma tarefa Celery específica."""
    result = AsyncResult(task_id, app=celery)
    info = {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
        "successful": result.successful(),
        "failed": result.failed(),
        "result": result.result if result.ready() else None,
        "traceback": result.traceback if result.failed() else None,
        "children": result.children,
    }
    logger.info(f"📍 Status da tarefa '{task_id}': {info}")
    return info

# === 📋 Tarefas Ativas ===
def list_active_tasks() -> dict:
    """Lista tarefas ativas (em execução)."""
    try:
        active = celery.control.inspect().active() or {}
        logger.info(f"🟢 Tarefas ativas: {active}")
        return active
    except Exception as e:
        logger.error(f"Erro ao listar tarefas ativas: {e}")
        return {"error": str(e)}

# === ⏳ Tarefas na Fila ===
def list_queued_tasks() -> dict:
    """Lista tarefas pendentes (scheduled + reserved)."""
    try:
        inspector = celery.control.inspect()
        scheduled = inspector.scheduled() or {}
        reserved = inspector.reserved() or {}
        queued = {**scheduled, **reserved}
        logger.info(f"📥 Tarefas na fila: {queued}")
        return queued
    except Exception as e:
        logger.error(f"Erro ao listar tarefas na fila: {e}")
        return {"error": str(e)}

# === ❌ Tarefas com Falha ===
def list_failed_tasks() -> dict:
    """Lista tarefas que falharam."""
    try:
        failed = celery.control.inspect().failed() or {}
        logger.warning(f"❌ Tarefas falhas: {failed}")
        return failed
    except Exception as e:
        logger.error(f"Erro ao listar falhas: {e}")
        return {"error": str(e)}

# === ✅ Tarefas Concluídas ===
def list_successful_tasks() -> dict:
    """Lista tarefas concluídas com sucesso."""
    try:
        successful = celery.control.inspect().successful() or {}
        logger.info(f"✅ Tarefas concluídas: {successful}")
        return successful
    except Exception as e:
        logger.error(f"Erro ao listar tarefas concluídas: {e}")
        return {"error": str(e)}

# === 🔁 Reiniciar Tarefas com Falha ===
def restart_failed_tasks() -> dict:
    """Reenvia tarefas falhas para execução novamente."""
    try:
        failed = celery.control.inspect().failed() or {}
        restarted = []

        for worker, tasks in failed.items():
            for task in tasks:
                task_id = task.get("id")
                task_name = task.get("name")
                args = task.get("args", [])
                kwargs = task.get("kwargs", {})

                if task_name:
                    try:
                        logger.warning(f"♻️ Reiniciando '{task_name}' (ID: {task_id})")
                        celery.send_task(task_name, args=args, kwargs=kwargs)
                        restarted.append(task_id)
                    except Exception as e:
                        logger.error(f"Erro ao reiniciar tarefa {task_id}: {e}")

        return {"restarted_tasks": restarted, "message": f"{len(restarted)} tarefas reenviadas"}
    except Exception as e:
        logger.error(f"Erro ao tentar reiniciar falhas: {e}")
        return {"error": str(e)}

# === 🛑 Revogar Tarefa ===
def revoke_task(task_id: str, terminate: bool = False) -> dict:
    """Revoga uma tarefa em andamento ou pendente."""
    try:
        celery.control.revoke(task_id, terminate=terminate)
        logger.warning(f"🛑 Tarefa revogada: {task_id} (terminate={terminate})")
        return {"task_id": task_id, "status": "revoked", "terminated": terminate}
    except Exception as e:
        logger.error(f"Erro ao revogar '{task_id}': {e}")
        return {"error": str(e)}

# === 📊 Estatísticas dos Workers ===
def get_worker_stats() -> dict:
    """Obtém estatísticas gerais dos workers."""
    try:
        stats = celery.control.inspect().stats() or {}
        logger.info(f"📈 Stats dos workers: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Erro ao buscar stats dos workers: {e}")
        return {"error": str(e)}

# === 🔍 Buscar por Nome ===
def find_tasks_by_name(name: str) -> list:
    """Procura tarefas ativas ou pendentes pelo nome."""
    try:
        inspector = celery.control.inspect()
        active = inspector.active() or {}
        reserved = inspector.reserved() or {}
        found = []

        for task_set in [active, reserved]:
            for worker, tasks in task_set.items():
                for task in tasks:
                    if name in task.get("name", ""):
                        found.append(task)
        logger.info(f"🔎 Tarefas com nome '{name}': {found}")
        return found
    except Exception as e:
        logger.error(f"Erro ao buscar por nome '{name}': {e}")
        return []

# === 📤 Exportar para CSV ===
def export_tasks_to_csv(tasks: list, filename: str = "tasks_export.csv") -> dict:
    """Exporta tarefas em formato CSV."""
    try:
        with NamedTemporaryFile(delete=False, mode="w", suffix=".csv") as tmp:
            writer = csv.DictWriter(tmp, fieldnames=tasks[0].keys())
            writer.writeheader()
            for task in tasks:
                writer.writerow(task)
            logger.info(f"📁 Exportado para: {tmp.name}")
            return {"csv_path": tmp.name}
    except Exception as e:
        logger.error(f"Erro ao exportar CSV: {e}")
        return {"error": str(e)}

# === 🔁 Cancelar Tudo ===
def reset_all_tasks() -> dict:
    """Revoga todas as tarefas pendentes ou em execução."""
    try:
        inspector = celery.control.inspect()
        active = inspector.active() or {}
        reserved = inspector.reserved() or {}
        revoked = []

        for task_group in [active, reserved]:
            for worker, tasks in task_group.items():
                for task in tasks:
                    task_id = task.get("id")
                    if task_id:
                        celery.control.revoke(task_id, terminate=True)
                        revoked.append(task_id)

        logger.warning(f"🔁 Todas tarefas revogadas: {len(revoked)}")
        return {"revoked_tasks": revoked, "message": f"{len(revoked)} tarefas canceladas"}
    except Exception as e:
        logger.error(f"Erro ao resetar tarefas: {e}")
        return {"error": str(e)}
