# 📁 backend/app/api/payments/webhook.py

import logging
import stripe

from fastapi import APIRouter, Request, Header, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.config import settings

# === Logger ===
logger = logging.getLogger(__name__)

# === Stripe Config ===
stripe.api_key = settings.stripe_secret_key
endpoint_secret = settings.stripe_secret_key

if not stripe.api_key or not endpoint_secret:
    raise RuntimeError("Stripe credentials ausentes.")

# === Router ===
router = APIRouter(prefix="/payments", tags=["Pagamentos"])

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db),
):
    if not stripe_signature:
        logger.warning("❌ Cabeçalho stripe-signature ausente.")
        raise HTTPException(status_code=400, detail="Cabeçalho stripe-signature ausente.")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=endpoint_secret,
        )
    except stripe.error.SignatureVerificationError:
        logger.warning("⚠️ Assinatura Stripe inválida.")
        raise HTTPException(status_code=400, detail="Assinatura Stripe inválida.")
    except Exception as e:
        logger.exception("❌ Erro ao processar webhook Stripe.")
        raise HTTPException(status_code=400, detail="Webhook inválido.")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_email")
        plan = session.get("metadata", {}).get("plan")

        if not customer_email or not plan:
            logger.error("❌ Webhook com dados incompletos.")
            return JSONResponse(status_code=400, content={"error": "Dados incompletos."})

        user = db.query(User).filter(User.email == customer_email).first()
        if user:
            user.plan = plan.lower()
            db.commit()
            logger.info(f"✅ Plano '{plan}' ativado para {customer_email}")
            return JSONResponse(status_code=200, content={"status": "ok"})
        else:
            logger.warning(f"⚠️ Usuário não encontrado para e-mail: {customer_email}")
            return JSONResponse(status_code=404, content={"error": "Usuário não encontrado."})

    logger.info(f"ℹ️ Evento não tratado: {event['type']}")
    return JSONResponse(status_code=200, content={"status": "ignored", "event": event["type"]})
