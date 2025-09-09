import os
import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.subscription import Subscription
from app.services.notifications import send_email_notification

# === 🔐 Configurações Stripe ===
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "https://elgn.ai/payment/success")
CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "https://elgn.ai/payment/cancel")

router = APIRouter(prefix="/payment", tags=["Billing"])

# 💳 Tabela temporária de preços (ideal migrar para banco de dados)
PLAN_PRICES = {
    "basic": {"name": "Plano Basic", "unit_amount": 1000},
    "pro": {"name": "Plano Pro", "unit_amount": 2500},
    "premium": {"name": "Plano Premium", "unit_amount": 5000},
    "empresarial": {"name": "Plano Empresarial", "unit_amount": 10000},
    "basic_anual": {"name": "Plano Basic Anual", "unit_amount": 10000},
    "pro_anual": {"name": "Plano Pro Anual", "unit_amount": 25000},
    "premium_anual": {"name": "Plano Premium Anual", "unit_amount": 50000},
    "empresarial_anual": {"name": "Plano Empresarial Anual", "unit_amount": 100000},
}


# === 🧾 Criar sessão de pagamento ===
@router.post("/create-checkout-session")
def create_checkout_session(
    plan: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🧾 Cria uma sessão Stripe para o plano selecionado.
    """
    plan_key = plan.lower().replace("-", "_")
    if plan_key not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail="Plano inválido.")

    try:
        plan_data = PLAN_PRICES[plan_key]

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=current_user.email,
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": plan_data["name"]},
                        "unit_amount": plan_data["unit_amount"],
                        "recurring": {
                            "interval": "year" if "anual" in plan_key else "month"
                        },
                    },
                    "quantity": 1,
                }
            ],
            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,
        )

        return {"checkout_url": session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar sessão Stripe: {e}")


# === ✅ Confirmar pagamento manual ===
@router.post("/confirm-payment")
def confirm_payment(
    plan: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Atualiza o plano do usuário após pagamento confirmado.
    """
    plan_key = plan.lower().replace("-", "_")
    if plan_key not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail="Plano inválido.")

    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()

        if not subscription:
            subscription = Subscription(
                user_id=current_user.id,
                plan=plan_key,
                payment_status="active"
            )
            db.add(subscription)
        else:
            subscription.plan = plan_key
            subscription.payment_status = "active"

        db.commit()

        # 📧 Enviar notificação por e-mail
        send_email_notification(
            to_email=current_user.email,
            subject="✅ Assinatura Ativada",
            message=(
                f"Olá {current_user.username},\n\n"
                f"Seu plano **{PLAN_PRICES[plan_key]['name']}** foi ativado com sucesso! 🎉\n"
                f"Agora você tem acesso total aos recursos do ELGN Video.AI.\n\n"
                "Obrigado por assinar! 🚀"
            )
        )

        return {"message": f"Plano {PLAN_PRICES[plan_key]['name']} ativado com sucesso."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao confirmar pagamento: {e}")
