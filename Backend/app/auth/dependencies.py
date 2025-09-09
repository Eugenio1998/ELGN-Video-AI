# 📁 app/auth/dependencies.py

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.jwt import SECRET_KEY, ALGORITHM

# === 🛡️ Configuração ===
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# === 🔐 Recupera usuário autenticado via token ===
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decodifica o token JWT, valida e retorna o usuário autenticado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais de autenticação inválidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            logger.warning("🔒 Token sem sub (ID de usuário ausente).")
            raise credentials_exception
        user_uuid = UUID(user_id)
    except (JWTError, ValueError) as e:
        logger.warning(f"🔒 Erro ao decodificar token JWT: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        logger.warning(f"🔒 Usuário com ID {user_id} não encontrado.")
        raise credentials_exception

    return user

# === 🛡️ Verifica se usuário tem o papel necessário ===
def require_role(*roles: UserRole):
    """
    Garante que o usuário tenha pelo menos um dos papéis especificados.
    """
    def check(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            logger.warning(f"🛑 Acesso negado para {current_user.username} (role: {current_user.role})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Requer um dos papéis: {[r.value for r in roles]}",
            )
        return current_user
    return check
