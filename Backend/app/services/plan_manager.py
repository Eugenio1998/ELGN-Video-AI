from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from app.models.subscription import Subscription

# === 🛠️ Logger padronizado ===
logger = logging.getLogger("plan_manager")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 🚀 Ativar Período de Teste ===
def activate_trial(user_id: int, db: Session) -> None:
    """Ativa o plano de teste por 7 dias para o usuário."""
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if not sub:
        logger.warning(f"🔍 Assinatura não encontrada | user_id={user_id}")
        return

    if sub.plan == "trial":
        logger.info(f"🟡 Plano de teste já ativo | user_id={user_id}")
        return

    sub.plan = "trial"
    sub.payment_status = "active"
    sub.last_payment_date = datetime.utcnow()
    sub.trial_expiration = datetime.utcnow() + timedelta(days=7)
    db.commit()

    logger.info(f"🧪 Trial ativado | user_id={user_id} | expira em {sub.trial_expiration}")

# === 📉 Downgrade automático após expiração ===
def downgrade_to_free_if_expired(user_id: int, db: Session) -> None:
    """Realiza downgrade automático se o plano de teste tiver expirado."""
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if not sub:
        logger.warning(f"🔍 Assinatura não encontrada | user_id={user_id}")
        return

    if sub.plan != "trial":
        logger.debug(f"ℹ️ Usuário não está em trial | user_id={user_id} | plano={sub.plan}")
        return

    if sub.trial_expiration and sub.trial_expiration < datetime.utcnow():
        sub.plan = "free"
        sub.payment_status = "expired"
        db.commit()
        logger.info(f"🔚 Trial expirado | user_id={user_id} | downgrade aplicado")
    else:
        logger.debug(f"⏳ Trial ainda ativo | user_id={user_id} | expira em {sub.trial_expiration}")

# === 🔁 Atualização de Plano ===
def upgrade_plan(user_id: int, new_plan: str, db: Session) -> None:
    """Atualiza o plano do usuário para um novo plano (Pro, Premium etc.)."""
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if not sub:
        logger.warning(f"🔍 Assinatura não encontrada | user_id={user_id}")
        return

    old_plan = sub.plan
    sub.plan = new_plan
    sub.payment_status = "active"
    sub.last_payment_date = datetime.utcnow()
    sub.trial_expiration = None
    db.commit()

    logger.info(f"🔼 Plano atualizado | user_id={user_id} | de '{old_plan}' para '{new_plan}'")

# === ❌ Cancelamento da Assinatura ===
def cancel_subscription(user_id: int, db: Session) -> None:
    """Cancela a assinatura atual do usuário."""
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if not sub:
        logger.warning(f"🔍 Assinatura não encontrada | user_id={user_id}")
        return

    sub.payment_status = "canceled"
    sub.end_date = datetime.utcnow()
    db.commit()

    logger.info(f"❌ Assinatura cancelada | user_id={user_id} | data={sub.end_date}")

# === 🔎 Consulta de Assinatura ===
def get_user_subscription(user_id: int, db: Session) -> Subscription:
    """Retorna o modelo de assinatura do usuário."""
    return db.query(Subscription).filter(Subscription.user_id == user_id).first()
