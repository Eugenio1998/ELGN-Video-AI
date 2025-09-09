# 📁 app/utils/logger.py

import logging
import sys

# === 🧠 Nome único e padronizado para evitar conflitos entre múltiplos imports ===
LOGGER_NAME = "elgn_logger"

# === 🔧 Configuração única do logger ===
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)
logger.propagate = (
    False  # Evita logs duplicados em alguns contextos como Celery ou Uvicorn
)

# === 🛠️ Configuração de handler se ainda não existir ===
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# === ✅ Funções utilitárias de log ===
def log_info(message: str) -> None:
    """📘 Loga mensagem informativa com prefixo visual."""
    logger.info(f"✅ {message}")


def log_error(message: str) -> None:
    """🛑 Loga mensagem de erro com prefixo visual."""
    logger.error(f"❌ {message}")


# === 📦 Exportações explícitas ===
__all__ = ["logger", "log_info", "log_error"]
