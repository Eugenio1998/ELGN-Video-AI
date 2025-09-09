from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from app.database import get_db
from app.auth.dependencies import require_role
from app.models.user import User, UserRole
from app.models.subscription import Subscription
from app.models.feedback import Feedback
from app.api.error_response import ErrorResponse

# === Modelos opcionais ===
try:
    from app.models.task_log import TaskLog
except ImportError:
    TaskLog = None

try:
    from app.models.video import Video
except ImportError:
    Video = None

# === Logger ===
logger = logging.getLogger(__name__)

# === Router ===
router = APIRouter(prefix="/admin", tags=["Admin"])

# === Schema de resposta ===
class AdminStatsResponse(BaseModel):
    users: int
    feedbacks: int
    active_subscriptions: int
    videos: int | None = None
    tasks: int | None = None

# === Endpoint: Estatísticas administrativas ===
@router.get(
    "/stats",
    response_model=AdminStatsResponse,
    summary="📊 Retorna estatísticas administrativas da plataforma",
    responses={403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Retorna dados agregados da plataforma para fins administrativos.
    Requer permissão de administrador.
    """
    try:
        user_count = db.query(User).count()
        feedback_count = db.query(Feedback).count()
        subscription_count = db.query(Subscription).filter(Subscription.status == "active").count()
        task_count = db.query(TaskLog).count() if TaskLog else None
        video_count = db.query(Video).count() if Video else None

        logger.info(f"📈 [admin:{current_user.id}] Consultou estatísticas administrativas.")

        return AdminStatsResponse(
            users=user_count,
            feedbacks=feedback_count,
            active_subscriptions=subscription_count,
            videos=video_count,
            tasks=task_count
        )

    except Exception as e:
        logger.error(f"❌ Erro ao recuperar estatísticas administrativas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao recuperar estatísticas.")
