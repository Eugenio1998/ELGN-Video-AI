from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from app.config import STRIPE_WEBHOOK_SECRET
from app.auth.dependencies import verify_webhook_signature
from app.database import get_db
from app.models import User, Subscription, Plan
from app.services.email_service import send_welcome_email
import logging, os

# === 💳 Stripe SDK ===
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
except ImportError:
    logging.warning("Stripe não instalado. Webhook limitado.")
except Exception as e:
    logging.error(f"Erro ao iniciar Stripe: {e}")

router = APIRouter(tags=["Webhooks"])

# === 📁 Logger ===
log_file = "logs/webhooks.log"
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("webhooks")

# === 🎯 Webhook Stripe ===
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: Session = Depends(get_db)):
    try:
        payload_bytes = await request.body()
        payload = payload_bytes.decode("utf-8")

        # 🔐 Verifica assinatura (se configurada)
        if STRIPE_WEBHOOK_SECRET:
            try:
                event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
            except ValueError:
                logger.error("❌ Payload inválido recebido.")
                raise HTTPException(status_code=400, detail="Payload inválido.")
            except stripe.error.SignatureVerificationError:
                logger.error("❌ Assinatura Stripe inválida.")
                raise HTTPException(status_code=400, detail="Assinatura inválida.")
        else:
            logger.warning("⚠️ STRIPE_WEBHOOK_SECRET não configurado. Ignorando verificação.")
            event = await request.json()

        event_type = event.get("type")
        logger.info(f"📥 Evento Stripe recebido: {event_type}")

        # === ✅ Pagamento confirmado ===
        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            metadata = session.get("metadata", {})
            customer_email = session.get("customer_details", {}).get("email")
            plan_name = metadata.get("plan", "").lower()
            subscription_id = session.get("subscription")

            if not customer_email or not plan_name:
                logger.error("❌ Dados incompletos na sessão Stripe.")
                raise HTTPException(status_code=400, detail="Dados incompletos na sessão Stripe.")

            user = db.query(User).filter(User.email == customer_email).first()
            if not user:
                logger.error(f"❌ Usuário '{customer_email}' não encontrado.")
                raise HTTPException(status_code=404, detail="Usuário não encontrado.")

            plan = db.query(Plan).filter(Plan.name.ilike(plan_name)).first()
            if not plan:
                logger.error(f"❌ Plano '{plan_name}' não encontrado.")
                raise HTTPException(status_code=404, detail="Plano não encontrado.")

            user.plan_id = plan.id
            if not user.subscription:
                user.subscription = Subscription(user_id=user.id, stripe_id=subscription_id, status="active")
            else:
                user.subscription.stripe_id = subscription_id
                user.subscription.status = "active"

            db.commit()
            send_welcome_email(user.email, user.username, plan.name)
            logger.info(f"✅ Assinatura confirmada | Email: {user.email} | Plano: {plan.name}")

        # === ❌ Pagamento falhou ===
        elif event_type == "invoice.payment_failed":
            invoice_id = event["data"]["object"]["id"]
            logger.warning(f"❌ Pagamento falhou | Invoice ID: {invoice_id}")

        # === 🔁 Atualização da assinatura ===
        elif event_type == "customer.subscription.updated":
            obj = event["data"]["object"]
            sub_id = obj["id"]
            status = obj["status"]

            subscription = db.query(Subscription).filter(Subscription.stripe_id == sub_id).first()
            if subscription:
                subscription.status = status
                db.commit()
                logger.info(f"🔄 Assinatura atualizada | Usuário: {subscription.user.email} | Status: {status}")

        # === 🗑️ Cancelamento da assinatura ===
        elif event_type == "customer.subscription.deleted":
            sub_id = event["data"]["object"]["id"]
            subscription = db.query(Subscription).filter(Subscription.stripe_id == sub_id).first()
            if subscription:
                subscription.status = "canceled"
                db.commit()
                logger.info(f"🗑️ Assinatura cancelada | Usuário: {subscription.user.email}")

        # === Outros eventos não tratados ===
        else:
            logger.info(f"ℹ️ Evento Stripe não tratado: {event_type}")

        return {"message": "Webhook processado com sucesso", "event": event_type}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"❌ Erro ao processar webhook Stripe: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar webhook Stripe.")
