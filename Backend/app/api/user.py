from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from app.database import get_db
from app.services.notifications import get_user_notifications
from app.services.plan_manager import downgrade_to_free_if_expired
from app.models.subscription import Subscription
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/user", tags=["User"])
logger = logging.getLogger(__name__)

# === SCHEMAS ===

class ProfileOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

class PlanOut(BaseModel):
    plan: str
    status: str
    trial_expiration: Optional[datetime] = None

class NotificationItem(BaseModel):
    message: str

class SEOCreditResponse(BaseModel):
    credits_remaining: int

# === ROTAS ===

@router.get(
    "/profile",
    response_model=ProfileOut,
    responses={401: {"model": ErrorResponse}}
)
def get_profile(current_user: User = Depends(get_current_user)):
    logger.info(f"👤 Consulta de perfil: {current_user.username}")
    return ProfileOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at
    )

@router.get(
    "/plan",
    response_model=PlanOut,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
def get_plan_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
        if not sub:
            logger.warning(f"⚠️ Assinatura não encontrada para {current_user.username}")
            raise HTTPException(status_code=404, detail="Assinatura não encontrada.")

        downgrade_to_free_if_expired(current_user.id, db)

        logger.info(f"📦 Plano consultado: {sub.plan} para {current_user.username}")
        return PlanOut(
            plan=sub.plan,
            status=sub.payment_status,
            trial_expiration=sub.trial_expiration
        )
    except Exception as e:
        logger.error(f"❌ Erro ao obter plano de {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter informações do plano.")

@router.get(
    "/notifications",
    response_model=List[NotificationItem],
    responses={401: {"model": ErrorResponse}}
)
def get_notifications(current_user: User = Depends(get_current_user)):
    logger.info(f"🔔 Notificações consultadas por {current_user.username}")
    messages = get_user_notifications(current_user.id)
    return [{"message": msg} for msg in messages]

@router.patch(
    "/seo-credits",
    response_model=SEOCreditResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
def update_seo_credits(
    decrement: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.seo_credits < decrement:
        logger.warning(f"⚠️ {current_user.username} tentou consumir {decrement} créditos sem saldo suficiente.")
        raise HTTPException(status_code=403, detail="Sem créditos suficientes.")

    try:
        current_user.seo_credits -= decrement
        db.commit()

        logger.info(f"✅ Crédito SEO consumido por {current_user.username}. Restante: {current_user.seo_credits}")
        return SEOCreditResponse(credits_remaining=current_user.seo_credits)

    except Exception as e:
        logger.error(f"❌ Erro ao atualizar créditos SEO para {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar os créditos SEO.")
