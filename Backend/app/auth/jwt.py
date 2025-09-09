# 📁 app/auth/jwt.py

from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
import logging

from app.config import settings

# === 🔐 Configurações ===
logger = logging.getLogger(__name__)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

if not SECRET_KEY:
    logger.critical("❗ SECRET_KEY não está definida. Isso é extremamente inseguro em produção!")

# === 🔐 Função para criar token de acesso ===
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Cria e retorna um token JWT válido por um tempo definido.
    Tempo padrão: 60 minutos (ou conforme configurado).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("✅ Token de acesso JWT gerado com sucesso.")
    return token

# === 🔐 Função para decodificar token ===
def decode_access_token(token: str) -> dict:
    """
    Decodifica o token JWT e retorna o payload.
    Lança erro se o token estiver expirado ou for inválido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not isinstance(payload, dict) or "sub" not in payload:
            logger.warning("⚠️ Token JWT decodificado sem campo 'sub'.")
            raise JWTError("Token inválido: campo 'sub' ausente.")
        logger.info(f"🔓 Token decodificado com sucesso. sub={payload.get('sub')}")
        return payload
    except ExpiredSignatureError:
        logger.warning("⏰ Token expirado.")
        raise JWTError("Token expirado.")
    except JWTError as e:
        logger.warning(f"🚫 Token inválido: {e}")
        raise
