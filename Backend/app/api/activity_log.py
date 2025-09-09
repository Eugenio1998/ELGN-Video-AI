from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, constr
import logging

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.activity_log import ActivityLog
from app.api.error_response import ErrorResponse

# === Logger ===
logger = logging.getLogger(__name__)

# === Router ===
router = APIRouter(prefix="/activity", tags=["Atividades"])

# === Schemas ===
class ActivityOut(BaseModel):
    id: int
    action: str
    detail: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True

class ActivityLogResponse(BaseModel):
    message: str
    id: int

# === Endpoint: Registrar atividade ===
@router.post(
    "/log",
    response_model=ActivityLogResponse,
    status_code=201,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
def log_activity(
    action: constr(min_length=2, max_length=64) = Query(..., description="Ação realizada (ex: 'apply_filter')"),
    detail: Optional[str] = Query(None, description="Detalhes adicionais (ex: 'filtro: grayscale')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registra uma atividade do usuário autenticado.
    """
    try:
        activity = ActivityLog(user_id=current_user.id, action=action, detail=detail)
        db.add(activity)
        db.commit()
        logger.info(f"✅ [user:{current_user.id}] Ação registrada: {action}")
        return {"message": "Atividade registrada com sucesso.", "id": activity.id}
    except Exception as e:
        logger.error(f"❌ Erro ao registrar atividade: {e}")
        raise HTTPException(status_code=500, detail="Erro ao registrar atividade.")

# === Endpoint: Histórico pessoal ===
@router.get(
    "/my",
    response_model=List[ActivityOut],
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
def get_my_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna o histórico de atividades do usuário autenticado.
    """
    try:
        logs = (
            db.query(ActivityLog)
            .filter(ActivityLog.user_id == current_user.id)
            .order_by(ActivityLog.timestamp.desc())
            .all()
        )
        logger.info(f"📜 [user:{current_user.id}] Consultou histórico pessoal")
        return logs
    except Exception as e:
        logger.error(f"❌ Erro ao buscar histórico: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar histórico.")

# === Endpoint: Histórico completo (admin) ===
@router.get(
    "/all",
    response_model=List[ActivityOut],
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
def get_all_activities(
    user_id: Optional[int] = Query(None, description="Filtrar por ID do usuário"),
    action: Optional[str] = Query(None, description="Filtrar por tipo de ação"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Deslocamento para paginação"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Retorna atividades de todos os usuários (admin only).
    """
    try:
        query = db.query(ActivityLog)
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        if action:
            query = query.filter(ActivityLog.action == action)

        logs = query.order_by(ActivityLog.timestamp.desc()).offset(offset).limit(limit).all()
        logger.info(f"📊 [admin:{current_user.id}] Consultou atividades (user_id={user_id}, action={action})")
        return logs
    except Exception as e:
        logger.error(f"❌ Erro ao buscar atividades: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar atividades.")
