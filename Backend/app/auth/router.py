# 📁 app/auth/router.py

import os
import json
import redis
import logging
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.database import get_db
from app.models.user import User
from app.auth.hashing import verify_password
from app.auth.jwt import create_access_token
from app.api.error_response import ErrorResponse
from app.auth.dependencies import get_current_user

# === ⚙️ Configurações ===
logger = logging.getLogger(__name__)
router = APIRouter()

# === 🔐 Redis ===
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_conn = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=2,
    decode_responses=True
)

# === 📧 SendGrid ===
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER", "elgn.video.ai@gmail.com")

# === 📦 Schemas ===
class LoginForm(BaseModel):
    email: str
    password: str

class Verify2FAForm(BaseModel):
    username: str
    otp_code: str

    @validator("otp_code")
    def validate_otp(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError("O código 2FA deve conter exatamente 6 dígitos numéricos.")
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    message: str
    username: str

# === 🔧 Funções auxiliares ===

def log_login_attempt(username: str, ip: str, status: str):
    log_data = {
        "username": username,
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat(),
        "status": status
    }
    redis_conn.rpush("login_attempts", json.dumps(log_data))

def log_failed_attempt(username: str, ip: str):
    key = f"failed_attempts:{username}"
    attempts = redis_conn.get(key)
    attempts = int(attempts) + 1 if attempts else 1
    redis_conn.setex(key, timedelta(minutes=15), attempts)
    if attempts >= 5:
        redis_conn.setex(f"blocked:{username}", 600, "blocked")
        log_login_attempt(username, ip, "🚫 Bloqueado por falhas repetidas.")

def is_user_blocked(username: str):
    return redis_conn.get(f"blocked:{username}") is not None

def send_otp_email(email: str, otp_code: str) -> bool:
    try:
        message = Mail(
            from_email=EMAIL_USER,
            to_emails=email,
            subject="🔐 Código de Verificação 2FA - ELGN",
            plain_text_content=f"Seu código de autenticação é: {otp_code}"
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        logger.info(f"📧 Código 2FA enviado para {email} via SendGrid.")
        return True
    except Exception as e:
        logger.error(f"❌ Falha ao enviar e-mail com SendGrid: {e}")
        return False

# === 🚀 Endpoints ===

@router.post("/verify-2fa", response_model=TokenResponse)
def verify_2fa(data: Verify2FAForm, db: Session = Depends(get_db)):
    code = redis_conn.get(f"2fa_{data.username}")

    logger.debug(f"🔍 Redis 2FA code: {code} vs. Input code: {data.otp_code}")

    if not code or code.strip() != data.otp_code.strip():
        logger.warning(f"❌ Código 2FA inválido para {data.username}")
        raise HTTPException(status_code=400, detail="Código inválido ou expirado.")

    redis_conn.delete(f"2fa_{data.username}")

    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        logger.warning(f"❌ Usuário não encontrado para username {data.username}")
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    token = create_access_token(data={"sub": str(user.id)})
    logger.info(f"✅ Token JWT emitido para {data.username}")
    return {"access_token": token, "token_type": "bearer"}

@router.get("/login-attempts")
def get_login_attempts():
    attempts = redis_conn.lrange("login_attempts", -50, -1)
    return [json.loads(a) for a in attempts]

@router.post("/unlock-user")
def unlock_user(username: str):
    redis_conn.delete(f"blocked:{username}")
    logger.info(f"🔓 Usuário desbloqueado manualmente: {username}")
    return {"message": f"Usuário {username} desbloqueado com sucesso."}

@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "plan": current_user.plan.name if current_user.plan else "free",
        "avatarUrl": current_user.avatar_url or "/img/user.png"
    }
auth_router = router
