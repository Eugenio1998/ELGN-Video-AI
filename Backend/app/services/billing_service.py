# 💳 Serviço de Faturamento com Stripe

import os
import logging
import stripe
from fastapi import HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.models.user import User

# === 🔐 Configuração Stripe ===
load_dotenv()
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY

# === 🛠 Logger ===
logger = logging.getLogger("billing_service")
logger.setLevel(logging.INFO)

# === 🎫 Consulta Status da Assinatura ===
def get_subscription_status(stripe_subscription_id: str) -> str:
    """Retorna o status atual da assinatura no Stripe."""
    try:
        subscription = stripe.Subscription.retrieve(stripe_subscription_id)
        return subscription["status"]
    except stripe.error.StripeError as e:
        logger.error(f"❌ StripeError ao buscar assinatura: {e}")
        raise HTTPException(status_code=400, detail="Erro ao consultar status da assinatura.")
    except Exception as e:
        logger.error(f"❌ Erro interno ao buscar assinatura: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao consultar assinatura.")

# === 🔄 Cancelamento de Assinatura ===
def cancel_subscription(stripe_subscription_id: str) -> dict:
    """Cancela a assinatura no final do período vigente."""
    try:
        subscription = stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True
        )
        logger.info(f"🔔 Assinatura marcada para cancelamento: {stripe_subscription_id}")
        return {
            "status": "cancel_at_period_end",
            "cancel_at": subscription.cancel_at
        }
    except stripe.error.StripeError as e:
        logger.error(f"❌ StripeError ao cancelar assinatura: {e}")
        raise HTTPException(status_code=400, detail="Erro ao cancelar assinatura.")
    except Exception as e:
        logger.error(f"❌ Erro interno ao cancelar assinatura: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao cancelar assinatura.")

# === ✅ Verificação de Plano Ativo ===
def is_plan_active(user: User, db: Session) -> bool:
    """
    Verifica se o plano do usuário está ativo com base no Stripe.
    Retorna True se 'active' ou 'trialing'.
    """
    try:
        if not user.stripe_subscription_id:
            return False
        status = get_subscription_status(user.stripe_subscription_id)
        return status in ["active", "trialing"]
    except Exception as e:
        logger.warning(f"⚠️ Erro ao verificar plano do usuário {user.id}: {e}")
        return False  # fallback de segurança
