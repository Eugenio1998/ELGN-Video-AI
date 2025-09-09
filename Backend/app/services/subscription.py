# 📁 backend/app/services/subscription.py

import os
import redis
import stripe
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from fastapi import HTTPException
from dotenv import load_dotenv

# === 🔧 Config ===
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)
PLAN_EXPIRATION_DAYS = int(os.getenv("PLAN_EXPIRATION_DAYS", 30))

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

tiers = {
    "free": {"price": 0, "limit": 10},
    "premium": {"price": 19.99, "limit": 100},
}

# === 🛠 Logger ===
logger = logging.getLogger("subscription")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === 📧 E-mail ===
def send_email(to_email: str, subject: str, message: str) -> bool:
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM]):
        logger.error("⚠️ Configurações de SMTP incompletas.")
        return False

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        logger.info(f"📨 E-mail enviado com sucesso para {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Falha ao enviar e-mail para {to_email}: {e}")
        return False

# === 💳 Criar checkout Stripe ===
def create_checkout_session(user_id: str, plan: str) -> str:
    if plan not in tiers:
        raise ValueError("Plano inválido.")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"{plan.capitalize()} Plan"},
                    "unit_amount": int(tiers[plan]["price"] * 100),
                },
                "quantity": 1,
            }],
            mode="subscription",
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
            metadata={"user_id": user_id, "plan": plan},
        )
        logger.info(f"✅ Checkout criado com sucesso: {session.url}")
        return session.url
    except stripe.error.StripeError as e:
        logger.error(f"❌ Erro Stripe: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no checkout: {str(e)}")

# === ❌ Cancelamento simples ===
def cancel_subscription_basic(user_id: str) -> str:
    subscription_id = redis_client.get(f"stripe_subscription:{user_id}")
    if not subscription_id:
        raise ValueError("Assinatura não encontrada.")

    try:
        stripe.Subscription.delete(subscription_id)
        _clear_subscription_data(user_id)
        logger.info(f"🗑️ Assinatura cancelada: {subscription_id}")
        return "Assinatura cancelada com sucesso."
    except stripe.error.StripeError as e:
        logger.error(f"Erro ao cancelar: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao cancelar: {str(e)}")

# === 💰 Cancelamento com reembolso ===
def cancel_subscription(user_id: str, user_email: str) -> str:
    subscription_id = redis_client.get(f"stripe_subscription:{user_id}")
    if not subscription_id:
        raise ValueError("Assinatura não encontrada.")

    refund_message = "Reembolso não realizado."
    try:
        invoices = stripe.Invoice.list(subscription=subscription_id, limit=1)
        if invoices and invoices.data:
            payment_intent_id = invoices.data[0].payment_intent
            if payment_intent_id:
                try:
                    refund = stripe.Refund.create(payment_intent=payment_intent_id)
                    refund_message = f"Reembolso realizado com sucesso (ID: {refund.id})."
                except stripe.error.StripeError as e:
                    refund_message = f"Erro ao reembolsar: {e}"

        stripe.Subscription.delete(subscription_id)
        _clear_subscription_data(user_id)

        send_email(
            user_email,
            "Cancelamento e Reembolso",
            f"Olá,\n\nSua assinatura foi cancelada.\n{refund_message}\n\nEquipe ELGN Video.AI"
        )
        return f"Assinatura cancelada. {refund_message}"
    except stripe.error.StripeError as e:
        logger.error(f"Erro no cancelamento com reembolso: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 🧹 Limpar dados Redis ===
def _clear_subscription_data(user_id: str) -> None:
    redis_client.set(f"subscription:{user_id}", "free")
    redis_client.delete(f"subscription_expiration:{user_id}")
    redis_client.delete(f"stripe_subscription:{user_id}")

# === 🔔 Webhook Stripe ===
def handle_stripe_webhook(event: dict) -> dict:
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})
    logger.info(f"📩 Webhook recebido: {event_type}")

    if event_type == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        plan = data.get("metadata", {}).get("plan")
        expiration = datetime.utcnow() + timedelta(days=PLAN_EXPIRATION_DAYS)
        if user_id and plan:
            redis_client.set(f"subscription:{user_id}", plan)
            redis_client.set(f"subscription_expiration:{user_id}", expiration.strftime("%Y-%m-%d"))
            redis_client.set(f"stripe_customer:{user_id}", data.get("customer"))
            redis_client.set(f"stripe_subscription:{user_id}", data.get("subscription"))

    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        _set_user_free_by_customer(customer_id)

    elif event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        customer_id = data.get("customer")
        status = data.get("status")
        if status == "canceled" or event_type.endswith("deleted"):
            _set_user_free_by_customer(customer_id)

    return {"status": "handled", "event": event_type}

# === 👥 Aux: reset por customer_id ===
def _set_user_free_by_customer(customer_id: str):
    user_id = next(
        (key.split(":")[-1] for key in redis_client.scan_iter("stripe_customer:*")
         if redis_client.get(key) == customer_id),
        None
    )
    if user_id:
        _clear_subscription_data(user_id)

# === 🔎 Verificação de status de assinatura (usado por scheduled_tasks) ===
def check_subscription_status(db=None):
    logger.info("🔍 Iniciando verificação de assinaturas salvas no Redis...")
    now = datetime.utcnow()

    for key in redis_client.scan_iter("subscription_expiration:*"):
        user_id = key.split(":")[-1]
        expiration_str = redis_client.get(key)

        try:
            expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d")
            if expiration_date < now:
                logger.info(f"⏰ Assinatura expirada para user_id={user_id}. Atualizando para 'free'.")
                _clear_subscription_data(user_id)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao processar user_id={user_id}: {e}")

    logger.info("✅ Verificação de assinaturas concluída.")
