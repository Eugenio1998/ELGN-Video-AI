# 📁 utils/login_protection.py

import json
import logging
import os
from datetime import datetime

import redis
from dotenv import load_dotenv

# === 🔧 Configuração de ambiente ===
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB_SECURITY = int(os.getenv("REDIS_DB_SECURITY", 2))
MAX_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
BLOCK_TIME = int(os.getenv("LOGIN_BLOCK_TIME", 600))  # segundos
ATTEMPT_EXPIRATION = int(
    os.getenv("LOGIN_ATTEMPT_EXPIRATION", 900)
)  # segundos

# === 🛠️ Logger ===
logger = logging.getLogger("login_protection")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === ☁️ Redis Connection ===
try:
    redis_conn = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB_SECURITY,
        decode_responses=True,
    )
    redis_conn.ping()
    logger.info("✅ Redis conectado (proteção de login)")
except redis.exceptions.ConnectionError as e:
    logger.error(f"❌ Erro ao conectar Redis: {e}")
    redis_conn = None

# === 🔐 Funções utilitárias ===


def is_user_blocked(username: str) -> bool:
    if not redis_conn:
        logger.warning("⚠️ Redis indisponível em is_user_blocked.")
        return False
    return redis_conn.exists(f"blocked:{username}") == 1


def block_user(username: str, ip: str) -> None:
    if not redis_conn:
        logger.warning("⚠️ Redis indisponível em block_user.")
        return
    redis_conn.setex(f"blocked:{username}", BLOCK_TIME, "blocked")
    log_data = {
        "username": username,
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "Usuário bloqueado após falhas consecutivas",
    }
    redis_conn.rpush("login_attempts", json.dumps(log_data))
    logger.warning(f"🚫 {username} bloqueado (IP: {ip}) por {BLOCK_TIME}s.")


def log_failed_attempt(username: str, ip: str) -> None:
    if not redis_conn:
        logger.warning("⚠️ Redis indisponível em log_failed_attempt.")
        return
    key = f"failed_attempts:{username}"
    attempts = int(redis_conn.get(key) or 0) + 1
    redis_conn.setex(key, ATTEMPT_EXPIRATION, attempts)
    logger.info(f"🔐 Falha de login: {username} ({attempts}/{MAX_ATTEMPTS})")

    if attempts >= MAX_ATTEMPTS:
        block_user(username, ip)

    redis_conn.rpush(
        "login_attempts",
        json.dumps(
            {
                "username": username,
                "ip": ip,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "Falha de login",
            }
        ),
    )


def clear_failed_attempts(username: str) -> None:
    if not redis_conn:
        logger.warning("⚠️ Redis indisponível em clear_failed_attempts.")
        return
    if redis_conn.delete(f"failed_attempts:{username}"):
        logger.info(f"🔓 Tentativas de falha removidas para: {username}")


def get_login_attempts_history(count: int = 10) -> list[dict]:
    if not redis_conn:
        logger.warning("⚠️ Redis indisponível em get_login_attempts_history.")
        return []
    try:
        entries = redis_conn.lrange("login_attempts", -count, -1)
        return [json.loads(entry) for entry in entries]
    except (redis.exceptions.RedisError, json.JSONDecodeError) as e:
        logger.error(f"❌ Erro ao carregar histórico de login: {e}")
        return []


# === 📦 Exportações explícitas ===
__all__ = [
    "is_user_blocked",
    "block_user",
    "log_failed_attempt",
    "clear_failed_attempts",
    "get_login_attempts_history",
]
