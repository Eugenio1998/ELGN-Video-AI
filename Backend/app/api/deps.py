import os
import logging
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.models.user import User
from app.database import get_db

# === 🔐 Configurações de segurança ===
load_dotenv()
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "elgn_fallback_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# === 🔑 Dependência de autenticação JWT ===

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Valida o token JWT do usuário autenticado e retorna o objeto User.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de acesso inválido ou ausente.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if not user_id or token_type != "access":
            logger.warning("Token malformado: sub ou type ausente/incorreto.")
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError) as e:
        logger.warning(f"❌ Erro ao decodificar token JWT: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning(f"⚠️ Token válido, mas usuário ID {user_id} não encontrado.")
        raise credentials_exception

    logger.info(f"🟢 Usuário autenticado: {user.username} (ID: {user.id})")
    return user
