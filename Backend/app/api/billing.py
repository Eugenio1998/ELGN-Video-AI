import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services import billing_service
from app.api.error_response import ErrorResponse

# === 🔧 Configurações ===
router = APIRouter(prefix="/billing", tags=["Assinaturas e Pagamentos"])
logger = logging.getLogger(__name__)

# === 📦 Schemas ===

class PlanOut(BaseModel):
    id: int
    name: str
    price: float
    description: str
    features: List[str]

class SubscriptionOut(BaseModel):
    plan_name: str
    status: str
    start_date: str
    end_date: Optional[str] = None
    payment_status: str
    is_active: Optional[bool] = True

class SubscribeIn(BaseModel):
    plan_id: int
    payment_method_token: str  # Token de pagamento simulado

class CancelResponse(BaseModel):
    message: str

# === 📋 Listagem de Planos ===

@router.get(
    "/plans",
    response_model=List[PlanOut],
    summary="Listar planos disponíveis"
)
def list_plans():
    """Lista todos os planos de assinatura disponíveis."""
    try:
        plans = billing_service.get_available_plans()
        logger.info("📦 Consulta de planos de assinatura realizada.")
        return plans
    except Exception as e:
        logger.error(f"❌ Erro ao listar planos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar os planos.")

# === 🧾 Assinar um plano ===

@router.post(
    "/subscribe",
    response_model=SubscriptionOut,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Assinar plano"
)
def subscribe_to_plan(
    subscription_data: SubscribeIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Assina um plano de assinatura com base no ID e token de pagamento simulado.
    """
    try:
        subscription = billing_service.subscribe_user_to_plan(
            user_id=current_user.id,
            plan_id=subscription_data.plan_id,
            payment_method_token=subscription_data.payment_method_token,
            db=db
        )
        logger.info(f"🟢 [{current_user.username}] assinou o plano {subscription.plan_name}")
        return subscription
    except ValueError as ve:
        logger.warning(f"⚠️ Assinatura inválida [{current_user.username}]: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"❌ Erro ao assinar plano {subscription_data.plan_id} para {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar a assinatura.")

# === 🔍 Ver assinatura atual ===

@router.get(
    "/subscription",
    response_model=SubscriptionOut,
    responses={404: {"model": ErrorResponse}},
    summary="Ver assinatura atual"
)
def get_user_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtém os detalhes da assinatura atual do usuário."""
    subscription = billing_service.get_user_subscription_details(
        user_id=current_user.id,
        db=db
    )
    if not subscription:
        logger.warning(f"⚠️ Assinatura não encontrada para [{current_user.username}]")
        raise HTTPException(status_code=404, detail="Assinatura não encontrada.")
    return subscription

# === ❌ Cancelar assinatura ===

@router.post(
    "/cancel",
    response_model=CancelResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Cancelar assinatura"
)
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancela a assinatura do usuário atual."""
    try:
        billing_service.cancel_user_subscription(
            user_id=current_user.id,
            db=db
        )
        logger.info(f"🔴 Assinatura cancelada por [{current_user.username}]")
        return {"message": "Assinatura cancelada com sucesso."}
    except Exception as e:
        logger.error(f"❌ Erro ao cancelar assinatura de [{current_user.username}]: {e}")
        raise HTTPException(status_code=500, detail="Erro ao cancelar a assinatura.")
