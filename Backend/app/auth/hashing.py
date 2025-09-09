# 📁 app/auth/hashing.py

import logging
from passlib.context import CryptContext

# === 🔐 Logger ===
logger = logging.getLogger(__name__)

# === 🔐 Contexto de criptografia para senhas (bcrypt) ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# === 🔐 Gerar hash seguro da senha ===
def hash_password(password: str) -> str:
    """
    Retorna o hash seguro da senha usando bcrypt.
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"❌ Erro ao hashear senha: {e}")
        raise

# === 🔐 Verificar correspondência entre senha e hash ===
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha informada corresponde ao hash armazenado.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao verificar senha: {e}")
        return False
