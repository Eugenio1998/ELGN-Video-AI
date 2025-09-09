import os
import json
import redis
import logging
from datetime import timedelta
from typing import Dict, Optional, Any, Union
from dotenv import load_dotenv

load_dotenv()

# === 📋 Logger Local ===
logger = logging.getLogger("push_register")
logger.setLevel(logging.INFO)

# === 🔌 Conexão Redis ===
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True
)

# === 🗝️ Prefixo de chave padrão ===
PUSH_PREFIX = "push_subscription"


# === 🔐 Registrar inscrição push ===
def register_push_subscription(user_id: str, subscription: Dict[str, Any]) -> bool:
    key = f"{PUSH_PREFIX}:{user_id}"
    try:
        redis_client.set(key, json.dumps(subscription))
        redis_client.expire(key, timedelta(days=30))
        logger.info(f"✅ Inscrição push registrada para o usuário {user_id}")
        return True
    except redis.RedisError as e:
        logger.error(f"❌ Erro Redis ao registrar inscrição push ({user_id}): {e}")
        return False


# === 📬 Obter inscrição push ===
def get_push_subscription(user_id: str) -> Optional[Dict[str, Any]]:
    key = f"{PUSH_PREFIX}:{user_id}"
    try:
        raw_data = redis_client.get(key)
        if raw_data:
            return json.loads(raw_data)
        logger.info(f"ℹ️ Nenhuma inscrição encontrada para o usuário {user_id}")
        return None
    except (redis.RedisError, json.JSONDecodeError) as e:
        logger.error(f"❌ Erro ao obter inscrição push ({user_id}): {e}")
        return None


# === ❌ Remover inscrição push ===
def remove_push_subscription(user_id: str) -> bool:
    key = f"{PUSH_PREFIX}:{user_id}"
    try:
        removed = redis_client.delete(key)
        if removed:
            logger.info(f"🗑️ Inscrição push removida para o usuário {user_id}")
            return True
        logger.info(f"ℹ️ Nenhuma inscrição push encontrada para o usuário {user_id}")
        return False
    except redis.RedisError as e:
        logger.error(f"❌ Erro ao remover inscrição push ({user_id}): {e}")
        return False


# === 🧾 Listar todas as inscrições push (admin/debug) ===
def list_all_push_subscriptions() -> Optional[Dict[str, Union[Dict[str, Any], str]]]:
    try:
        keys = redis_client.keys(f"{PUSH_PREFIX}:*")
        result = {}

        for key in keys:
            user_id = key.split(":")[1]
            try:
                subscription_raw = redis_client.get(key)
                if subscription_raw:
                    result[user_id] = json.loads(subscription_raw)
            except json.JSONDecodeError as je:
                logger.warning(f"⚠️ Erro de JSON para chave {key}: {je}")
                result[user_id] = "Erro ao decodificar JSON"

        return result

    except redis.RedisError as e:
        logger.error(f"❌ Erro ao listar inscrições push: {e}")
        return None
