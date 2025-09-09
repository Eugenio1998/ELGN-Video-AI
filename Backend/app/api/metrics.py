import logging
from fastapi import APIRouter, Response, Depends, HTTPException
from sqlalchemy.orm import Session
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST

from app.database import get_db
from app.models.user import User
from app.models.feedback import Feedback
from app.models.subscription import Subscription
from app.models.video import Video
from app.models.task_log import TaskLog

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/", summary="Expor métricas Prometheus")
def metrics(db: Session = Depends(get_db)):
    """
    📊 Rota de exportação de métricas compatível com Prometheus.
    """
    try:
        registry = CollectorRegistry()

        Gauge("elgn_users_total", "Total de usuários", registry=registry).set(
            db.query(User).count()
        )
        Gauge("elgn_feedback_total", "Total de feedbacks", registry=registry).set(
            db.query(Feedback).count()
        )
        Gauge("elgn_active_subscriptions", "Total de planos ativos", registry=registry).set(
            db.query(Subscription).filter(Subscription.status == "active").count()
        )
        Gauge("elgn_videos_total", "Total de vídeos enviados", registry=registry).set(
            db.query(Video).count()
        )
        Gauge("elgn_tasks_total", "Total de tarefas IA executadas", registry=registry).set(
            db.query(TaskLog).count()
        )

        logger.info("✅ Métricas Prometheus geradas com sucesso.")
        return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

    except Exception as e:
        logger.error(f"❌ Erro ao coletar métricas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar métricas.")
