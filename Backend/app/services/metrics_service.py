# 📊 Serviço de Métricas de Uso (Redis)

import redis
import logging
from datetime import datetime
from typing import Dict, List
from app.config import settings

# === 🛠️ Logger ===
logger = logging.getLogger("metrics_service")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 🔌 Conexão Redis ===
try:
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("📊✅ Conexão com Redis estabelecida com sucesso (métricas).")
except redis.exceptions.ConnectionError as e:
    logger.error(f"📊❌ Erro ao conectar com Redis (métricas): {e}")
    redis_client = None

# === 🔍 Utilitário: Buscar chaves ===
def _get_keys_by_pattern(pattern: str) -> List[str]:
    if not redis_client:
        logger.error("📊❌ Redis indisponível para busca de chaves.")
        return []
    try:
        return redis_client.keys(pattern)
    except redis.exceptions.RedisError as e:
        logger.error(f"📊❌ Erro ao buscar chaves com pattern '{pattern}': {e}")
        return []

# === 📈 Logar uso de IA ===
def log_ia_usage(user_id: str, action: str, expire_seconds: int = 86400) -> None:
    if not redis_client:
        logger.error("📊❌ Redis indisponível para log de uso.")
        return

    today = datetime.utcnow().date()
    key = f"metrics:usage:{user_id}:{today}"
    try:
        redis_client.hincrby(key, action, 1)
        redis_client.expire(key, expire_seconds)
        logger.info(f"📊🟢 Uso registrado | Usuário: {user_id} | Ação: {action} | Data: {today}")
    except redis.exceptions.RedisError as e:
        logger.error(f"📊❌ Erro ao registrar uso: {e}")

# === 📅 Consultar uso por data ===
def get_ia_usage(user_id: str, date_str: str) -> Dict[str, str]:
    if not redis_client:
        logger.error("📊❌ Redis indisponível para consulta.")
        return {}

    key = f"metrics:usage:{user_id}:{date_str}"
    try:
        usage = redis_client.hgetall(key)
        logger.info(f"📊📅 Uso de IA | Usuário: {user_id} | Data: {date_str} | Ações: {usage}")
        return usage
    except redis.exceptions.RedisError as e:
        logger.error(f"📊❌ Erro ao buscar uso em {date_str}: {e}")
        return {}

# === 📋 Resumo diário de todos os usuários ===
def get_daily_usage_summary(date_str: str) -> Dict[str, Dict[str, str]]:
    if not redis_client:
        logger.error("📊❌ Redis indisponível para gerar resumo.")
        return {}

    pattern = f"metrics:usage:*:{date_str}"
    summary = {}
    try:
        keys = _get_keys_by_pattern(pattern)
        for key in keys:
            parts = key.split(":")
            if len(parts) >= 4:
                user_id = parts[2]
                summary[user_id] = redis_client.hgetall(key)
        logger.info(f"📊📋 Resumo de uso diário | Data: {date_str} | Usuários: {len(summary)}")
        return summary
    except redis.exceptions.RedisError as e:
        logger.error(f"📊❌ Erro ao gerar resumo diário: {e}")
        return {}

# === 📦 Total acumulado por usuário ===
def get_total_usage(user_id: str) -> Dict[str, int]:
    if not redis_client:
        logger.error("📊❌ Redis indisponível para cálculo acumulado.")
        return {}

    pattern = f"metrics:usage:{user_id}:*"
    total: Dict[str, int] = {}
    try:
        keys = _get_keys_by_pattern(pattern)
        for key in keys:
            usage = redis_client.hgetall(key)
            for action, count in usage.items():
                total[action] = total.get(action, 0) + int(count)
        logger.info(f"📊📦 Uso acumulado | Usuário: {user_id} | Total: {total}")
        return total
    except redis.exceptions.RedisError as e:
        logger.error(f"📊❌ Erro ao somar uso acumulado: {e}")
        return {}
