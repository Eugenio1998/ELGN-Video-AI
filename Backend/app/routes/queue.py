from fastapi import APIRouter, HTTPException, Depends
import redis
import logging
import os

from rq import Queue
from rq.job import Job
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter(tags=["Admin"])

# === 🧠 Logger configurado
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === 🔧 Configuração Redis / RQ
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
queue = Queue("video_processing", connection=redis_conn)

# === 📊 Verificar status da fila
@router.get("/queue/status", dependencies=[Depends(require_role(UserRole.ADMIN))])
def queue_status(current_user: User = Depends(get_current_user)):
    """
    Retorna o status de todos os jobs na fila de processamento de vídeo.
    Apenas admins podem consultar.
    """
    try:
        jobs = queue.jobs
        job_status = [
            {
                "id": job.id,
                "status": job.get_status(),
                "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "ended_at": job.ended_at.isoformat() if job.ended_at else None,
                "description": job.description,
            }
            for job in jobs
        ]
        logger.info(f"📊 {len(jobs)} jobs encontrados por {current_user.username}")
        return {"total_jobs": len(jobs), "jobs": job_status}

    except Exception as e:
        logger.exception("❌ Erro ao consultar fila de jobs.")
        raise HTTPException(status_code=500, detail="Erro ao consultar fila.")


# === ❌ Cancelar job da fila
@router.post("/queue/cancel", dependencies=[Depends(require_role(UserRole.ADMIN))])
def cancel_job(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Cancela um job com ID fornecido. Somente jobs em 'queued' ou 'deferred' podem ser cancelados.
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        if job and job.get_status() in ["queued", "deferred"]:
            job.cancel()
            logger.info(f"🛑 Job cancelado: {job_id} por {current_user.username}")
            return {"message": f"Job {job_id} cancelado com sucesso."}

        raise HTTPException(status_code=404, detail="Job não encontrado ou já processado.")
    except Exception as e:
        logger.exception(f"❌ Erro ao cancelar job {job_id}")
        raise HTTPException(status_code=500, detail="Erro ao cancelar job.")


# === 🔁 Reprocessar job com falha
@router.post("/queue/reprocess", dependencies=[Depends(require_role(UserRole.ADMIN))])
def reprocess_job(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Reprocessa um job com status 'failed'.
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        if job.get_status() != "failed":
            raise HTTPException(status_code=400, detail="Job não está com status 'failed'.")

        func = job.func_name
        args = job.args or ()
        kwargs = job.kwargs or {}
        new_job = queue.enqueue(func, *args, **kwargs)
        logger.info(f"🔁 Job {job_id} reprocessado como novo job {new_job.id}")
        return {"message": f"Job reprocessado com sucesso: novo ID {new_job.id}"}

    except Exception as e:
        logger.exception(f"❌ Erro ao reprocessar job {job_id}")
        raise HTTPException(status_code=500, detail="Erro ao reprocessar job.")
