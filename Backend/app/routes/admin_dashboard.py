import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import redis
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import require_role
from app.database import get_db
from app.models.user import User, UserRole
from app.models.subscription import Subscription, PlanEnum
from app.models.video import Video
from app.core.config import settings  # ⬅️ novo: uso centralizado de configs

# ==== 🚀 Router ====
router = APIRouter()
logger = logging.getLogger(__name__)

# ==== 🧠 Redis Client ====
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True
    )
except Exception as e:
    logger.error(f"❌ Redis connection error: {e}")
    raise RuntimeError("Falha ao conectar ao Redis.")

# ==== 💰 Preço do plano ====
try:
    PREMIUM_PLAN_PRICE = float(settings.PREMIUM_PLAN_PRICE)
except Exception as e:
    logger.warning(f"⚠️ Erro ao obter preço do plano: {e}")
    PREMIUM_PLAN_PRICE = 19.99


# === 🔍 Visão Geral do Sistema ===
@router.get("/overview", response_model=Dict[str, int], dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_admin_overview(db: Session = Depends(get_db)):
    try:
        return {
            "total_users": db.query(User).count(),
            "total_premium_users": db.query(Subscription).filter(Subscription.plan == PlanEnum.PREMIUM).count(),
            "total_videos": db.query(Video).count()
        }
    except Exception as e:
        logger.error(f"❌ Erro em /overview: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas gerais.")


# === 👥 Listar Usuários com Filtros ===
@router.get("/users", response_model=List[Dict[str, Any]], dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_all_users(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    plan: Optional[PlanEnum] = Query(None)
):
    try:
        query = db.query(User)
        if start_date and end_date:
            query = query.filter(User.created_at.between(start_date, end_date))
        if plan:
            query = query.join(Subscription).filter(Subscription.plan == plan)

        return [
            {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "is_active": user.is_active,
                "name": user.name,
                "role": user.role.value
            } for user in query.all()
        ]
    except Exception as e:
        logger.error(f"❌ Erro em /users: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar usuários.")


# === 💳 Pagamentos ===
@router.get("/payments", response_model=List[Dict[str, Any]], dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_payment_status(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    try:
        query = db.query(Subscription)
        if start_date and end_date:
            query = query.filter(Subscription.last_payment_date.between(start_date, end_date))

        return [
            {
                "id": sub.id,
                "user_id": sub.user_id,
                "plan": sub.plan.value,
                "last_payment_date": sub.last_payment_date.isoformat() if sub.last_payment_date else None,
                "is_active": sub.is_active
            } for sub in query.all()
        ]
    except Exception as e:
        logger.error(f"❌ Erro em /payments: {e}")
        raise HTTPException(status_code=500, detail="Erro ao consultar pagamentos.")


# === 📊 Receita ===
@router.get("/revenue", response_model=Dict[str, Any], dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_revenue_statistics(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        revenue_data = (
            db.query(func.date(Subscription.last_payment_date), func.count(Subscription.id))
            .filter(Subscription.plan == PlanEnum.PREMIUM, Subscription.last_payment_date >= start_date)
            .group_by(func.date(Subscription.last_payment_date))
            .order_by(func.date(Subscription.last_payment_date))
            .all()
        )
        return {
            "revenue_stats": {
                str(date): round(count * PREMIUM_PLAN_PRICE, 2)
                for date, count in revenue_data
            }
        }
    except Exception as e:
        logger.error(f"❌ Erro em /revenue: {e}")
        raise HTTPException(status_code=500, detail="Erro ao calcular estatísticas de receita.")


# === 📈 Uso via Redis ===
@router.get("/usage", response_model=Dict[str, Any], dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_usage_statistics():
    try:
        today = datetime.today().date()
        keys = redis_client.keys(f"usage:*:{today}")
        usage_data = [
            {
                "user_id": key.split(":")[1],
                "usage_count": int(redis_client.get(key))
            }
            for key in keys
        ]
        return {
            "date": str(today),
            "usage": usage_data
        }
    except Exception as e:
        logger.error(f"❌ Erro em /usage: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas de uso.")
