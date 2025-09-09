# 📁 services/security.py

import logging
from app.utils.login_protection import (
    is_user_blocked,
    log_failed_attempt,
    clear_failed_attempts,
    get_login_attempts_history
)


# === 🛡️ Segurança Centralizada ===
logger = logging.getLogger("security_service")

def verificar_bloqueio_usuario(username: str) -> bool:
    return is_user_blocked(username)

def registrar_falha_login(username: str, ip: str) -> None:
    log_failed_attempt(username, ip)

def limpar_falhas_usuario(username: str) -> None:
    clear_failed_attempts(username)

def historico_tentativas_login(limit: int = 10) -> list[dict]:
    return get_login_attempts_history(limit)
