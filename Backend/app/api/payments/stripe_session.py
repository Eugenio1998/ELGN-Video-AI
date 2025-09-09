# 📁 backend/app/api/payments/stripe_session.py

import logging
import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Literal

from app.config import settings

# === Logger ===
logger = logging.getLogger(__name__)

# === Stripe Key ===
stripe.api_key = settings.stripe_secret_key
if not stripe.api_key:
    raise RuntimeError("STRIPE_SECRET_KEY não configurada.")

# === Router ===
router = APIRouter(prefix="/payments", tags=["Pagamentos"])

# === Schema ===
class StripeSessionRequest(BaseModel):
    plan: Literal["basic", "pro", "premium", "empresarial"]
    email: EmailStr

@router.post("/stripe-session")
async def create_stripe_session(payload: StripeSessionRequest):
    try:
        prices = {
            "basic": 1000,
            "pro": 2500,
            "premium": 5000,
            "empresarial": 10000
        }

        amount = prices.get(payload.plan)
        if not amount:
            raise HTTPException(status_code=400, detail="Plano inválido.")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=payload.email,
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Plano {payload.plan.title()} - ELGN Video.AI"},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            metadata={"plan": payload.plan},
            success_url=f"{settings.FRONTEND_URL}/thanks?success=true",
            cancel_url=f"{settings.FRONTEND_URL}/plans?canceled=true",
        )

        logger.info(f"💳 Sessão Stripe criada para {payload.email} | Plano: {payload.plan}")
        return {"url": session.url}

    except stripe.error.StripeError as e:
        logger.exception("Erro Stripe.")
        raise HTTPException(status_code=502, detail="Erro ao criar sessão no Stripe.")
    except Exception as e:
        logger.exception("Erro inesperado na criação da sessão Stripe.")
        raise HTTPException(status_code=500, detail="Erro interno ao criar sessão.")
