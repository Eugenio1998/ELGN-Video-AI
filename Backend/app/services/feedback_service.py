# 💬 Serviço de Feedbacks via Redis

import redis
import logging
from uuid import uuid4
from typing import List, Dict, Optional
from redis.exceptions import RedisError, ConnectionError
from app.config import settings

# === 🛠 Logger ===
logger = logging.getLogger("feedback_service")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 🔌 Inicializar Redis ===
REDIS_FEEDBACK_PREFIX = "feedback"
try:
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("💬✅ Conexão com Redis estabelecida (feedback).")
except ConnectionError as e:
    logger.error(f"💬❌ Falha ao conectar com Redis (feedback): {e}")
    redis_client = None

# === 🔑 Utilitários ===
def build_key(feedback_id: str) -> str:
    return f"{REDIS_FEEDBACK_PREFIX}:{feedback_id}"

def get_all_keys() -> List[str]:
    return redis_client.keys(f"{REDIS_FEEDBACK_PREFIX}:*") if redis_client else []

# === 💾 Armazenar Feedback ===
def store_feedback(user_id: str, content: str, rating: int = 5) -> Optional[str]:
    """Armazena um feedback no Redis com expiração de 30 dias."""
    if not redis_client:
        logger.error("💬❌ Redis indisponível.")
        return None

    if not (1 <= rating <= 5):
        logger.warning(f"💬⚠️ Rating inválido: {rating}")
        rating = 5

    feedback_id = str(uuid4())
    key = build_key(feedback_id)
    try:
        redis_client.hset(key, mapping={
            "user_id": user_id,
            "content": content,
            "rating": rating
        })
        redis_client.expire(key, 60 * 60 * 24 * 30)  # 30 dias
        logger.info(f"💬✅ Feedback salvo | user={user_id}, id={feedback_id}, rating={rating}")
        return feedback_id
    except RedisError as e:
        logger.error(f"💬❌ Erro ao salvar feedback | user={user_id}: {e}")
        return None

# === 📋 Listar Todos os Feedbacks ===
def get_all_feedback() -> List[Dict[str, str]]:
    """Retorna todos os feedbacks armazenados no Redis."""
    if not redis_client:
        logger.error("💬❌ Redis indisponível.")
        return []

    try:
        keys = get_all_keys()
        feedbacks = [redis_client.hgetall(k) for k in keys]
        logger.info(f"💬📋 Total de feedbacks: {len(feedbacks)}")
        return feedbacks
    except RedisError as e:
        logger.error(f"💬❌ Erro ao recuperar feedbacks: {e}")
        return []

# === 🔍 Buscar por ID ===
def get_feedback_by_id(feedback_id: str) -> Optional[Dict[str, str]]:
    """Busca um feedback pelo ID."""
    if not redis_client:
        logger.error("💬❌ Redis indisponível.")
        return None

    try:
        key = build_key(feedback_id)
        data = redis_client.hgetall(key)
        if data:
            logger.info(f"💬🔎 Feedback encontrado | ID: {feedback_id}")
            return data
        else:
            logger.warning(f"💬⚠️ Feedback não encontrado | ID: {feedback_id}")
            return None
    except RedisError as e:
        logger.error(f"💬❌ Erro ao buscar feedback ID={feedback_id}: {e}")
        return None

# === 🧽 Deletar por ID ===
def delete_feedback(feedback_id: str) -> bool:
    """Remove um feedback do Redis pelo ID."""
    if not redis_client:
        logger.error("💬❌ Redis indisponível.")
        return False

    try:
        key = build_key(feedback_id)
        deleted = redis_client.delete(key)
        if deleted:
            logger.info(f"💬🧹 Feedback deletado | ID: {feedback_id}")
            return True
        else:
            logger.warning(f"💬⚠️ Feedback não encontrado para deletar | ID: {feedback_id}")
            return False
    except RedisError as e:
        logger.error(f"💬❌ Erro ao deletar feedback ID={feedback_id}: {e}")
        return False

# === 🔎 Buscar por Usuário ===
def get_feedback_by_user(user_id: str) -> List[Dict[str, str]]:
    """Retorna todos os feedbacks enviados por um usuário específico."""
    if not redis_client:
        logger.error("💬❌ Redis indisponível.")
        return []

    try:
        results = []
        for key in get_all_keys():
            feedback = redis_client.hgetall(key)
            if feedback.get("user_id") == user_id:
                results.append(feedback)
        logger.info(f"💬📥 Feedbacks do usuário {user_id}: {len(results)}")
        return results
    except RedisError as e:
        logger.error(f"💬❌ Erro ao buscar feedbacks do usuário {user_id}: {e}")
        return []
