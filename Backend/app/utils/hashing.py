# 📁 app/utils/hashing.py

from passlib.context import CryptContext

# === 🔒 Contexto de criptografia ===
pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


# === ✅ Verifica se a senha em texto corresponde à senha criptografada ===
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara a senha fornecida com o hash armazenado.

    Args:
        plain_password (str): Senha em texto plano.
        hashed_password (str): Hash armazenado.

    Returns:
        bool: True se a senha for válida, False se não for.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False  # Segurança: evita quebra em caso de hash inválido


# === 🔐 Gera o hash seguro da senha ===
def get_password_hash(password: str) -> str:
    """
    Retorna o hash da senha fornecida.

    Args:
        password (str): Senha em texto plano.

    Returns:
        str: Hash seguro da senha.
    """
    return pwd_context.hash(password)


# === 📦 Exportações explícitas ===
__all__ = ["verify_password", "get_password_hash"]
