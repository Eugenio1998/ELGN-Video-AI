# 📁 backend/app/routes/subscription.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import redis

from app.services.subscription import create_checkout_session, cancel_subscription, redis_client
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User

# === 📌 Configuração ===
router = APIRouter(tags=["Assinaturas"])
logger = logging.getLogger("subscription")
logger.setLevel(logging.INFO)

# === 🔐 Validação de identidade ===
def ensure_same_user(requesting_user: User, target_user_id: str):
    if str(requesting_user.id) != target_user_id:
        logger.warning(f"⛔ Acesso negado: {requesting_user.username} tentou agir como {target_user_id}")
        raise HTTPException(status_code=403, detail="Ação não autorizada para outro usuário.")

# === 🛒 Criar sessão de checkout ===
@router.post("/subscribe/{user_id}")
def subscribe(user_id: str, plan: str, current_user: User = Depends(get_current_user)):
    """
    📦 Cria uma sessão de checkout para o plano escolhido.
    """
    ensure_same_user(current_user, user_id)
    try:
        checkout_url = create_checkout_session(user_id, plan)
        logger.info(f"🧾 Sessão de checkout criada | user_id={user_id} | plano={plan}")
        return {"checkout_url": checkout_url}
    except ValueError as e:
        logger.error(f"⚠️ Erro de valor | {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"❌ Erro inesperado ao criar checkout | user_id={user_id}")
        raise HTTPException(status_code=500, detail="Erro ao criar sessão de assinatura.")

# === 📅 Obter status da assinatura ===
@router.get("/subscription/{user_id}")
def get_subscription_status(user_id: str, current_user: User = Depends(get_current_user)):
    """
    📊 Retorna o plano e status da assinatura atual do usuário.
    """
    ensure_same_user(current_user, user_id)

    try:
        plan = redis_client.get(f"subscription:{user_id}") or "free"
        expiration_str = redis_client.get(f"subscription_expiration:{user_id}") or "N/A"
        expired = False
        expiration = "N/A"

        if expiration_str != "N/A":
            try:
                expiration_dt = datetime.strptime(expiration_str, "%Y-%m-%d")
                expired = expiration_dt < datetime.utcnow()
                if expired:
                    plan = "free"
                expiration = expiration_str
            except ValueError:
                logger.warning(f"📅 Erro ao converter data de expiração: '{expiration_str}'")

        logger.info(
            f"📊 Status assinatura | user_id={user_id} | plano={plan} | expiração={expiration} | expirado={expired}"
        )
        return {
            "user_id": user_id,
            "plan": plan,
            "expiration": expiration,
            "expired": expired
        }

    except redis.RedisError as e:
        logger.error(f"💥 Redis Error | {e}")
        raise HTTPException(status_code=500, detail="Erro ao acessar o cache de assinaturas.")
    except Exception as e:
        logger.exception("❌ Erro inesperado ao obter status de assinatura.")
        raise HTTPException(status_code=500, detail="Erro ao obter status de assinatura.")

# === ❌ Cancelar assinatura ===
@router.post("/cancel/{user_id}")
def cancel_user_subscription(user_id: str, current_user: User = Depends(get_current_user)):
    """
    🛑 Cancela a assinatura ativa do usuário.
    """
    ensure_same_user(current_user, user_id)

    try:
        message = cancel_subscription(user_id)
        logger.info(f"🛑 Assinatura cancelada | user_id={user_id}")
        return {"message": message}
    except ValueError as e:
        logger.error(f"⚠️ Erro ao cancelar assinatura: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("❌ Erro inesperado ao cancelar assinatura.")
        raise HTTPException(status_code=500, detail="Erro ao cancelar assinatura.")
