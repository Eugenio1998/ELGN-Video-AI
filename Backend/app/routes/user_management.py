from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
import redis
import smtplib
import os
import logging
from email.message import EmailMessage

from app.models.user import User
from app.database import get_db
from app.auth.hashing import hash_password, verify_password
from app.auth.jwt import create_access_token

router = APIRouter(tags=["User"])

# === 🔌 Redis ===
redis_conn = redis.Redis(host="localhost", port=6379, db=5, decode_responses=True)

# === 📧 Configurações de E-mail ===
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "seuemail@gmail.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "senha")

# === 🧾 Logger ===
logger = logging.getLogger("user_management")

# === 📦 Schemas ===
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class ResetRequest(BaseModel):
    email: EmailStr

class ResetConfirm(BaseModel):
    token: str
    new_password: str

# === 👤 Cadastro de usuário ===
@router.post("/users/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Nome de usuário já registrado.")
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="E-mail já registrado.")

        hashed_pw = hash_password(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_pw,
            role=user.role,
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"🟢 Novo usuário registrado: {new_user.username} (ID: {new_user.id})")
        return {"message": "Usuário criado com sucesso.", "user_id": new_user.id}

    except Exception as e:
        logger.exception("❌ Erro ao registrar usuário.")
        raise HTTPException(status_code=500, detail="Erro interno ao registrar usuário.")

# === 🔐 Login ===
@router.post("/users/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            logger.warning(f"🔒 Tentativa de login inválido: {user.username}")
            raise HTTPException(status_code=401, detail="Credenciais inválidas.")

        token = create_access_token(data={"sub": db_user.username})
        logger.info(f"✅ Login realizado: {db_user.username}")
        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        logger.exception("❌ Erro no login.")
        raise HTTPException(status_code=500, detail="Erro interno no login.")

# === 📃 Listar usuários ===
@router.get("/users/list")
def list_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        return [
            {"id": u.id, "username": u.username, "email": u.email, "role": u.role}
            for u in users
        ]
    except Exception as e:
        logger.exception("❌ Erro ao listar usuários.")
        raise HTTPException(status_code=500, detail="Erro interno ao listar usuários.")

# === 🗑️ Deletar usuário ===
@router.delete("/users/delete/{username}")
def delete_user(username: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        db.delete(user)
        db.commit()
        logger.info(f"🗑️ Usuário deletado: {username}")
        return {"message": "Usuário deletado com sucesso."}

    except Exception as e:
        logger.exception(f"❌ Erro ao deletar usuário: {username}")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar usuário.")

# === 📩 Solicitação de redefinição de senha ===
@router.post("/users/reset-request")
def request_password_reset(data: ResetRequest):
    try:
        token = secrets.token_urlsafe(16)
        redis_conn.setex(f"reset_token:{token}", 600, data.email)

        msg = EmailMessage()
        msg["Subject"] = "Redefinição de Senha - ELGN AI"
        msg["From"] = EMAIL_USER
        msg["To"] = data.email
        msg.set_content(
            f"Você solicitou uma redefinição de senha.\n\n"
            f"Use este token: {token}\n\n"
            f"Ele expira em 10 minutos."
        )

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        logger.info(f"📨 Token de redefinição enviado para: {data.email}")
        return {"message": "Token de redefinição enviado para o e-mail informado."}

    except Exception as e:
        logger.exception("❌ Erro ao enviar e-mail de redefinição.")
        raise HTTPException(status_code=500, detail="Erro interno ao enviar e-mail.")

# === 🔐 Confirmação da redefinição ===
@router.post("/users/reset-confirm")
def confirm_password_reset(data: ResetConfirm, db: Session = Depends(get_db)):
    try:
        email = redis_conn.get(f"reset_token:{data.token}")
        if not email:
            raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        user.hashed_password = hash_password(data.new_password)
        db.commit()
        redis_conn.delete(f"reset_token:{data.token}")

        logger.info(f"🔑 Senha redefinida para: {user.username}")
        return {"message": "Senha redefinida com sucesso."}

    except Exception as e:
        logger.exception("❌ Erro ao redefinir senha.")
        raise HTTPException(status_code=500, detail="Erro interno ao redefinir senha.")
