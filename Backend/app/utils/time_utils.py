# 📁 app/utils/time_utils.py

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("time_utils")


# === 🕓 Horário atual em UTC ===
def utc_now() -> datetime:
    """
    Retorna o horário atual em UTC.
    """
    return datetime.utcnow()


# === 🧾 Formata datetime como string ===
def format_timestamp(dt: Optional[datetime]) -> str:
    """
    Formata um datetime como string: YYYY-MM-DD HH:MM:SS
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""


# === 📅 ISO 8601 atual ===
def isoformat_now() -> str:
    """
    Retorna o datetime atual como string ISO 8601 com sufixo 'Z' (UTC).
    Exemplo: '2025-06-21T13:45:00Z'
    """
    return datetime.utcnow().isoformat() + "Z"


# === 📅 Converte para ISO 8601 ===
def to_isoformat(dt: Optional[datetime]) -> str:
    """
    Converte um datetime para formato ISO 8601. Retorna string vazia se None.
    """
    return dt.isoformat() if dt else ""


# === ⏱️ Converte datetime para Unix timestamp ===
def to_unix(dt: datetime) -> int:
    """
    Converte um datetime para timestamp Unix (segundos desde 1970-01-01).
    """
    return int(dt.timestamp())


# === 🔁 Converte string → datetime ===
def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Converte string no formato 'YYYY-MM-DD HH:MM:SS' para datetime.

    Raises:
        ValueError: Se o formato estiver inválido.
    """
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")


# === 🔁 Versão segura do parse ===
def parse_timestamp_safe(timestamp_str: str) -> Optional[datetime]:
    """
    Converte string para datetime, retornando None se falhar.
    """
    try:
        return parse_timestamp(timestamp_str)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao converter timestamp: {e}")
        return None


# === 📦 Exportações explícitas ===
__all__ = [
    "utc_now",
    "format_timestamp",
    "isoformat_now",
    "to_isoformat",
    "to_unix",
    "parse_timestamp",
    "parse_timestamp_safe",
]
