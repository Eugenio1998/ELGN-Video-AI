# 📁 backend/app/routes/auth/secure_login.py

from fastapi import APIRouter, HTTPException, Request, Depends, Form
from sqlalchemy.orm import Session
from app.auth.hashing import verify_password
from app.models.user import User
from app.auth.dependencies import get_db
from app.services.security import is_user_blocked
from app.routes.security import log_suspicious_activity

import logging

router = APIRouter(tags=["Auth"])
logger = logging.getLogger("secure_login")
logger.setLevel(logging.INFO)

# === 🔐 Endpoint de login com segurança reforçada ===
@router.post("/auth/secure-login")
def secure_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    🔐 Login seguro com verificação de IP, bloqueio por tentativas e auditoria de falhas.
    """
    user_ip = request.headers.get("X-Forwarded-For") or request.client.host or "unknown"
    username = username.strip().lower()

    try:
        user = db.query(User).filter_by(username=username).first()

        # 🚫 Credenciais inválidas
        if not user or not verify_password(password, user.hashed_password):
            log_suspicious_activity(username, user_ip, "❌ Credenciais inválidas")
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

        # ⛔ Verificação de bloqueio
        if is_user_blocked(username):
            log_suspicious_activity(username, user_ip, "🚫 Tentativa de login durante bloqueio")
            raise HTTPException(status_code=403, detail="Usuário bloqueado temporariamente")

        # ✅ Login autorizado
        logger.info(f"✅ Login seguro aprovado para '{username}' | IP: {user_ip}")
        return {"message": "Login seguro validado com sucesso"}

    except HTTPException:
        raise  # repassa a exceção sem mascarar o código HTTP
    except Exception as e:
        logger.exception(f"❌ Erro interno ao tentar autenticar '{username}': {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao realizar login")
