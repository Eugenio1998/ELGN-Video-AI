# 📁 backend/app/services/usage_limits.py

import redis
import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Optional
from sqlalchemy.orm import Session
from app.models.subscription import Subscription

# === ⚙️ Configurações ===
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB_USAGE", 0))

FREE_PLAN_LIMIT = int(os.getenv("FREE_PLAN_LIMIT", 10))
PREMIUM_PLAN_LIMIT = int(os.getenv("PREMIUM_PLAN_LIMIT", 100))

# === 🧠 Setup Redis ===
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    redis_client.ping()
except redis.exceptions.ConnectionError as e:
    raise RuntimeError(f"❌ Falha ao conectar ao Redis: {e}")

# === 🛠️ Logger ===
logger = logging.getLogger("usage_limits")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === 🧾 Buscar Plano do Usuário ===
def get_user_plan_from_db(user_id: str, db: Session) -> str:
    """
    Obtém o plano mais recente do usuário a partir do banco de dados.
    """
    try:
        sub = db.query(Subscription).filter_by(user_id=user_id).order_by(Subscription.created_at.desc()).first()
        return sub.plan if sub else "free"
    except Exception as e:
        logger.error(f"❌ Erro ao buscar plano do usuário {user_id}: {e}")
        return "free"

# === 🚦 Checar e Atualizar Uso ===
def check_and_update_usage(user_id: str, db: Session, plan: Optional[str] = None) -> dict:
    """
    Verifica e atualiza o uso do dia com base no plano do usuário.
    """
    today_key = f"elgn:usage:{user_id}:{datetime.today().date()}"
    plan = plan or get_user_plan_from_db(user_id, db)
    limit = FREE_PLAN_LIMIT if plan == "free" else PREMIUM_PLAN_LIMIT

    logger.debug(f"🔎 Verificando uso de '{user_id}' ({plan}) - Limite: {limit} - Chave: {today_key}")
    try:
        usage = redis_client.incr(today_key)

        if usage == 1:
            redis_client.expire(today_key, timedelta(days=1))
            logger.debug(f"📅 TTL definido para 24h em '{today_key}'")

        if usage > limit:
            logger.warning(f"🚫 Limite excedido: {usage}/{limit} para usuário {user_id}")
            return {"allowed": False, "used": usage - 1, "limit": limit}

        return {"allowed": True, "used": usage, "limit": limit}
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro no Redis para uso de {user_id}: {e}")
        return {"allowed": False, "used": -1, "limit": limit, "error": str(e)}

# === 🔁 Resetar Uso ===
def reset_usage(user_id: str, date: Optional[datetime] = None) -> dict:
    """
    Reseta o uso do usuário para a data especificada (ou hoje).
    """
    date_to_reset = (date or datetime.today()).date()
    key_to_delete = f"elgn:usage:{user_id}:{date_to_reset}"

    try:
        deleted = redis_client.delete(key_to_delete)
        logger.info(f"🗑️ Uso de '{user_id}' resetado para {date_to_reset}: {'sim' if deleted else 'não encontrado'}")
        return {"reset": bool(deleted), "key_deleted": key_to_delete}
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao resetar uso do usuário {user_id}: {e}")
        return {"reset": False, "error": str(e)}

# === 📊 Obter Uso Atual ===
def get_current_usage(user_id: str, db: Session) -> dict:
    """
    Retorna o uso atual do usuário no dia.
    """
    today_key = f"elgn:usage:{user_id}:{datetime.today().date()}"
    try:
        usage = redis_client.get(today_key)
        plan = get_user_plan_from_db(user_id, db)
        limit = FREE_PLAN_LIMIT if plan == "free" else PREMIUM_PLAN_LIMIT
        return {"used": int(usage or 0), "limit": limit}
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao obter uso do usuário {user_id}: {e}")
        return {"used": -1, "limit": 0, "error": str(e)}
