import logging
from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.notifications import send_email_notification, store_email_log
from app.models.subscription import Subscription

# === 🛠️ Logger padronizado ===
logger = logging.getLogger("payment_notifications")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 📬 Notificação de pagamento por e-mail ===
def notify_user(email: str, subject: str, message: str, user_id: Optional[str] = None) -> None:
    """Envia e registra uma notificação de pagamento por e-mail."""
    if not email:
        logger.warning(f"📭 E-mail não fornecido | user_id={user_id} | notificação não enviada.")
        return

    success = send_email_notification(email, subject, message)
    status = "sucesso" if success else "erro"

    if user_id:
        store_email_log(user_id, subject, status)

    logger.info(f"📧 Notificação enviada | email={email} | user_id={user_id} | assunto='{subject}' | status={status}")

# === ⚙️ Atualiza status da assinatura e envia notificação ===
def process_payment_status(
    user_id: str,
    email: str,
    status: str,
    plan: str,
    db: Session = Depends(get_db)
) -> dict:
    """Atualiza o status da assinatura no banco e envia notificação ao usuário."""
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()

    if not subscription:
        logger.warning(f"❌ Assinatura não encontrada | user_id={user_id}")
        return {"message": "Assinatura não encontrada"}

    subscription.payment_status = status
    subscription.plan = plan
    db.commit()

    logger.info(f"📦 Assinatura atualizada | user_id={user_id} | status={status} | plano={plan}")

    subject = "Atualização de assinatura"
    if status == "active":
        message = f"🎉 Seu plano {plan.capitalize()} foi ativado com sucesso!"
    elif status == "canceled":
        message = "Sua assinatura foi cancelada. Você voltou ao plano gratuito."
    else:
        message = f"O status da sua assinatura foi atualizado para: {status}."

    notify_user(email, subject, message, user_id)
    return {"message": "Status da assinatura atualizado com sucesso."}
