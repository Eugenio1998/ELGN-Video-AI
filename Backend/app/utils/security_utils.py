# 📁 app/utils/security_utils.py

import logging
import secrets
import string

# === 📋 Logger configurado ===
logger = logging.getLogger("security_utils")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# === 🔐 Geração de token seguro ===
def generate_token(
    length: int = 32, use_symbols: bool = False, exclude_similar: bool = False
) -> str:
    """
    Gera um token seguro aleatório.

    Args:
        length (int): Número de caracteres do token (mínimo 8 recomendado).
        use_symbols (bool): Se True, inclui caracteres especiais (!@#$%).
        exclude_similar (bool): Se True, remove caracteres ambíguos (O/0, l/1, etc).

    Returns:
        str: Token aleatório seguro.
    """
    if not isinstance(length, int) or length < 8:
        raise ValueError(
            "Token muito curto. Recomenda-se no mínimo 8 caracteres."
        )

    base_chars = string.ascii_letters + string.digits

    if use_symbols:
        base_chars += "!@#$%&*()-_=+"

    if exclude_similar:
        for c in "Il1O0":
            base_chars = base_chars.replace(c, "")

    token = "".join(secrets.choice(base_chars) for _ in range(length))

    logger.debug(f"🔐 Token gerado com {length} caracteres.")

    return token


# === 📦 Exportações explícitas ===
__all__ = ["generate_token"]
