import os
import json
import redis
import logging
from datetime import timedelta
from dotenv import load_dotenv
from typing import Any, Callable

# === 🔧 Carregar variáveis de ambiente ===
load_dotenv()

# === 🛠️ Logger ===
logger = logging.getLogger("redis_cache")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 🔌 Conexão com Redis ===
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=int(os.getenv("REDIS_DB", 0)),
        decode_responses=True,
    )
    redis_client.ping()
    logger.info("✅ Conexão com Redis estabelecida para o serviço de cache.")
except redis.exceptions.ConnectionError as e:
    logger.error(f"❌ Erro ao conectar com Redis: {e}")
    redis_client = None

# === 📥 Armazenar dado no cache ===
def cache_set(key: str, data: Any, expiration: int = 3600, prefix: str = "default") -> bool:
    namespaced_key = f"{prefix}:{key}"
    if redis_client is None:
        logger.error("❌ Falha ao armazenar: Redis não disponível.")
        return False
    try:
        redis_client.setex(namespaced_key, timedelta(seconds=expiration), json.dumps(data))
        logger.debug(f"💾 Cache set: {namespaced_key} (expiração: {expiration}s)")
        return True
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao salvar no cache ({namespaced_key}): {e}")
        return False

# === 📤 Obter dado do cache ===
def cache_get(key: str, prefix: str = "default") -> Any:
    namespaced_key = f"{prefix}:{key}"
    if redis_client is None:
        logger.error("❌ Falha ao obter: Redis não disponível.")
        return None
    try:
        cached_data = redis_client.get(namespaced_key)
        if cached_data:
            return json.loads(cached_data)
        logger.debug(f"⚠️ Chave não encontrada no cache: {namespaced_key}")
        return None
    except (redis.exceptions.RedisError, json.JSONDecodeError) as e:
        logger.error(f"❌ Erro ao ler cache ({namespaced_key}): {e}")
        return None

# === ❌ Apagar item do cache ===
def cache_delete(key: str, prefix: str = "default") -> bool:
    namespaced_key = f"{prefix}:{key}"
    if redis_client is None:
        logger.error("❌ Falha ao deletar: Redis não disponível.")
        return False
    try:
        result = redis_client.delete(namespaced_key)
        if result > 0:
            logger.debug(f"🗑️ Cache deletado: {namespaced_key}")
            return True
        logger.debug(f"⚠️ Chave para deletar não encontrada: {namespaced_key}")
        return False
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao deletar chave ({namespaced_key}): {e}")
        return False

# === ⏱️ Ver TTL ===
def cache_ttl(key: str, prefix: str = "default") -> int:
    namespaced_key = f"{prefix}:{key}"
    if redis_client is None:
        logger.error("❌ Redis não disponível para TTL.")
        return -2
    try:
        return redis_client.ttl(namespaced_key)
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao consultar TTL ({namespaced_key}): {e}")
        return -2

# === 🔍 Verifica existência ===
def cache_exists(key: str, prefix: str = "default") -> bool:
    namespaced_key = f"{prefix}:{key}"
    if redis_client is None:
        logger.error("❌ Redis não disponível para verificação de existência.")
        return False
    try:
        return redis_client.exists(namespaced_key) > 0
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao verificar existência ({namespaced_key}): {e}")
        return False

# === 🧹 Limpar prefixo ===
def cache_clear(prefix: str = "default") -> int:
    if redis_client is None:
        logger.error("❌ Redis não disponível para limpeza de cache.")
        return 0
    try:
        keys = redis_client.keys(f"{prefix}:*")
        if keys:
            deleted = redis_client.delete(*keys)
            logger.info(f"🧹 {deleted} itens removidos com prefixo '{prefix}'")
            return deleted
        logger.info(f"ℹ️ Nenhuma chave encontrada com prefixo '{prefix}'")
        return 0
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao limpar cache com prefixo '{prefix}': {e}")
        return 0

# === 🧠 Get or Set (função) ===
def cache_get_or_set(
    key: str,
    compute_func: Callable[[], Any],
    ttl: int = 3600,
    prefix: str = "default"
) -> Any:
    namespaced_key = f"{prefix}:{key}"
    if redis_client is None:
        logger.warning("⚠️ Redis indisponível. Executando fallback.")
        return compute_func()
    try:
        cached = redis_client.get(namespaced_key)
        if cached:
            return json.loads(cached)
        result = compute_func()
        redis_client.setex(namespaced_key, ttl, json.dumps(result))
        logger.info(f"✅ Resultado computado e armazenado no cache: {namespaced_key}")
        return result
    except Exception as e:
        logger.error(f"❌ Erro em cache_get_or_set ({namespaced_key}): {e}")
        return compute_func()