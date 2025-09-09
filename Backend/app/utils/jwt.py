# 📁 app/utils/jwt.py

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

# === 🛡️ Logger ===
logger = logging.getLogger(__name__)

# === 🔐 Configurações de segurança ===
SECRET_KEY = os.getenv("SECRET_KEY", "elgn-default-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12


# === 🧾 Cria um token JWT com dados customizados e expiração ===
def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Gera um JWT assinado contendo os dados informados.

    Args:
        data (dict): Dados a serem codificados no token (ex: user_id, role).
        expires_delta (timedelta, opcional): Tempo de validade do token. Usa padrão se não informado.

    Returns:
        str: Token JWT gerado.
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        )
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"🔐 Token gerado com expiração em {expire}")
        return token
    except Exception as e:
        logger.error(f"❌ Erro ao gerar token JWT: {e}")
        raise

    # === 🔍 Decodifica um token JWT e retorna os dados ou None ===
def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        logger.error(f"❌ Erro ao decodificar token JWT: {e}")
        return None



# === 📦 Exportações explícitas ===
__all__ = ["create_access_token"]
