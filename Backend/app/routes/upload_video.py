# 📁 backend/app/routes/upload_video.py

from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends
from celery.result import AsyncResult
from uuid import uuid4
import os
import logging
from pydantic import BaseModel, constr
from app.auth.dependencies import get_current_user
from app.services.video_tasks import (
    process_video_high_priority,
    process_video_low_priority,
    process_scene_split_video,
    celery_app,
    active_tasks_gauge,
    scheduled_tasks_gauge,
    reserved_tasks_gauge,
    PROCESSED_DIR,
    ALERT_THRESHOLD,
    log_history,
)
from app.utils.alerts import send_alert_email

router = APIRouter()
MAX_FILE_SIZE_MB = 200
ALLOWED_EXTENSIONS = {"mp4", "mov", "webm"}

class UploadVideoInput(BaseModel):
    priority: constr(strip_whitespace=True)

def validate_video_upload(file: UploadFile):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

    return ext

# === 🎥 Upload comum com prioridade ===
@router.post("/upload/video/")
async def upload_video(
    file: UploadFile,
    priority: str = Form("low"),
    current_user=Depends(get_current_user)
):
    try:
        ext = validate_video_upload(file)
        contents = await file.read()
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(status_code=400, detail="Arquivo excede 200MB.")

        validated = UploadVideoInput(priority=priority)
        output_path = os.path.join(PROCESSED_DIR, os.path.basename(file.filename))
        with open(output_path, "wb") as f:
            f.write(contents)

        task = (
            process_video_high_priority if validated.priority == "high"
            else process_video_low_priority
        ).apply_async(args=[output_path, output_path])

        return {
            "message": "Processamento iniciado",
            "output_path": output_path,
            "priority": validated.priority,
            "task_id": task.id
        }

    except Exception as e:
        logging.error(f"Erro no upload de vídeo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ✂️ Upload para corte automático por cenas ===
@router.post("/upload/video/split-by-scenes")
async def split_video_upload(
    file: UploadFile,
    current_user=Depends(get_current_user)
):
    try:
        ext = validate_video_upload(file)
        contents = await file.read()
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(status_code=400, detail="Arquivo excede 200MB.")

        input_path = os.path.join(PROCESSED_DIR, f"temp_{uuid4()}.{ext}")
        with open(input_path, "wb") as f:
            f.write(contents)

        task = process_scene_split_video.apply_async(args=[input_path, str(current_user.id)])
        return {"message": "Corte por cenas iniciado", "task_id": task.id}

    except Exception as e:
        logging.error(f"Erro no upload de corte por cenas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 📌 Status da task ===
@router.get("/queue/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    logging.info(f"Status da tarefa {task_id}: {task_result.status}")
    log_history(f"Status da tarefa {task_id}: {task_result.status}")
    result = task_result.result
    if isinstance(result, Exception):
        return {"task_id": task_id, "status": task_result.status, "result": str(result)}
    return {"task_id": task_id, "status": task_result.status, "result": result}

# === 📈 Monitoramento de tarefas Celery ===
@router.get("/queue/monitor")
async def monitor_queue():
    try:
        i = celery_app.control.inspect()
        active = i.active() or {}
        scheduled = i.scheduled() or {}
        reserved = i.reserved() or {}
    except Exception as e:
        logging.error(f"Erro ao monitorar fila: {e}")
        return {"error": str(e)}

    active_count = sum(len(t) for t in active.values())
    scheduled_count = sum(len(t) for t in scheduled.values())
    reserved_count = sum(len(t) for t in reserved.values())

    active_tasks_gauge.set(active_count)
    scheduled_tasks_gauge.set(scheduled_count)
    reserved_tasks_gauge.set(reserved_count)

    logging.info(f"Fila monitorada: {active_count} ativas, {scheduled_count} agendadas, {reserved_count} reservadas.")
    log_history(f"Fila monitorada: {active_count} ativas, {scheduled_count} agendadas, {reserved_count} reservadas.")

    if active_count > ALERT_THRESHOLD:
        send_alert_email("🚨 Alerta de Fila", f"Tarefas ativas excederam limite: {active_count} (> {ALERT_THRESHOLD})")

    return {
        "active_tasks": active,
        "scheduled_tasks": scheduled,
        "reserved_tasks": reserved
    }
