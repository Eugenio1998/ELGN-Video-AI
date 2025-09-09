# 📁 app/auth/utils.py

import os
import json
import redis
import random
import logging
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from jose import jwt
from passlib.context import CryptContext

# === ⚙️ Configurações e conexões ===
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 2))

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.seuprovedor.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "seu-email@dominio.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "sua-senha")

SECRET_KEY = os.getenv("SECRET_KEY", "default-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# === 🔐 Senha ===

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# === 🔑 JWT ===

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# === 🔢 OTP / 2FA ===

def generate_otp(username: str) -> str:
    code = str(random.randint(100000, 999999))
    redis_conn.setex(f"2fa:{username}", timedelta(minutes=5), code)
    return code

def validate_otp(username: str, otp_code: str) -> bool:
    stored = redis_conn.get(f"2fa:{username}")
    if stored and stored == otp_code:
        redis_conn.delete(f"2fa:{username}")
        return True
    return False

def send_otp_email(email: str, otp_code: str) -> bool:
    try:
        msg = EmailMessage()
        msg["Subject"] = "🔐 Seu código de autenticação (2FA)"
        msg["From"] = EMAIL_USER
        msg["To"] = email
        msg.set_content(
            f"Seu código de autenticação é: {otp_code}\n"
            f"Ele expira em 5 minutos.\n\n"
            f"Equipe ELGN"
        )

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        logger.info(f"📧 Código 2FA enviado para {email}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao enviar e-mail para {email}: {e}")
        return False

# === 🚫 Tentativas e bloqueios ===

MAX_ATTEMPTS = 5
BLOCK_TIME = 600  # 10 minutos

def log_login_attempt(username: str, ip: str, status: str):
    data = {
        "username": username,
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat(),
        "status": status
    }
    redis_conn.rpush("login_attempts", json.dumps(data))

def get_login_attempts(limit: int = 50):
    entries = redis_conn.lrange("login_attempts", -limit, -1)
    return [json.loads(e) for e in entries]

def register_failed_attempt(username: str) -> int:
    key = f"failed:{username}"
    attempts = int(redis_conn.get(key) or 0) + 1
    redis_conn.setex(key, timedelta(minutes=15), attempts)
    return attempts

def is_user_blocked(username: str) -> bool:
    return redis_conn.exists(f"blocked:{username}")

def block_user(username: str, ip: str):
    redis_conn.setex(f"blocked:{username}", BLOCK_TIME, "1")
    logger.warning(f"🚫 Usuário {username} bloqueado por {BLOCK_TIME}s (IP: {ip})")
    log_login_attempt(username, ip, f"🚫 Bloqueado por {BLOCK_TIME}s")

def unblock_user(username: str):
    redis_conn.delete(f"blocked:{username}")
    logger.info(f"🔓 Usuário desbloqueado: {username}")
