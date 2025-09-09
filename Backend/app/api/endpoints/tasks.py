# 📁 backend/app/api/endpoints/task.py

import time
import logging
from typing import Optional, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from celery import shared_task, current_task

from app.celery_app import celery_app
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/tasks")
logger = logging.getLogger(__name__)

# === 📦 Esquema de Resposta ===

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: Optional[float] = None

# === 🔍 Endpoint: Consultar Status de uma Task Celery ===

@router.get(
    "/{task_id}",
    response_model=TaskStatusResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["Tarefas"]
)
async def get_task_status(task_id: str):
    """
    Consulta o status atual de execução de uma task Celery.
    Retorna progresso se disponível.
    """
    try:
        result = AsyncResult(task_id, app=celery_app)

        task_info = result.info if isinstance(result.info, dict) else {}
        progress = task_info.get("percent") if result.state == "PROGRESS" else None
        error = str(result.traceback) if result.failed() else None
        final_result = result.result if result.ready() and not result.failed() else None

        response = TaskStatusResponse(
            task_id=task_id,
            status=result.status,
            result=final_result,
            error=error,
            progress=progress
        )

        logger.info(f"📊 Status da task {task_id} → {result.status}")
        return response
    except Exception as e:
        logger.exception(f"❌ Erro ao consultar status da task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao consultar status da tarefa.")

# === 🧪 Task de Teste: Simula Execução com Progresso ===

@shared_task(bind=True)
def long_running_task(self, total_steps: int):
    """
    Simula uma execução longa para testes de barra de progresso.
    """
    for i in range(total_steps):
        time.sleep(1)
        percent_complete = ((i + 1) / total_steps) * 100
        self.update_state(state="PROGRESS", meta={"percent": percent_complete})
    return {"result": "Tarefa concluída com sucesso!"}
