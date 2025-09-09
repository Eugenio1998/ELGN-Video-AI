# 📁 app/utils/file_utils.py

import logging
import os
import shutil
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

TEMP_DIR = "/tmp/elgn_ai_temp"


# === ✅ Garante que o diretório temporário exista ===
def ensure_temp_dir_exists() -> None:
    """Cria o diretório temporário se ele ainda não existir."""
    try:
        os.makedirs(TEMP_DIR, exist_ok=True)
    except Exception as e:
        logger.exception(f"❌ Falha ao criar diretório temporário: {e}")
        raise


# === 🗑️ Remove uma pasta inteira ===
def remove_dir(path: str) -> None:
    """Remove o diretório informado, se existir."""
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
        logger.info(f"📁 Diretório removido: {path}")


# === 📄 Remove um único arquivo ===
def remove_file(path: str) -> None:
    """Remove um arquivo específico, se existir."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"🗑️ Arquivo removido: {path}")
    except Exception as e:
        logger.exception(f"❌ Erro ao remover arquivo {path}: {e}")


# === 🧼 Limpa arquivos temporários (filtrando por extensão) ===
def clear_temp_dir(filter_ext: Optional[str] = None) -> None:
    """Remove arquivos do diretório temporário, com ou sem filtro por extensão."""
    try:
        if os.path.exists(TEMP_DIR):
            for filename in os.listdir(TEMP_DIR):
                path = os.path.join(TEMP_DIR, filename)
                if os.path.isfile(path) and (
                    not filter_ext or filename.endswith(filter_ext)
                ):
                    os.remove(path)
            logger.info(f"🧹 Diretório temporário limpo: {TEMP_DIR}")
    except Exception as e:
        logger.exception(
            f"❌ Erro ao limpar diretório temporário {TEMP_DIR}: {e}"
        )


# === 📍 Gera caminho de arquivo único para uso temporário ===
def generate_temp_file_path(ext: str = "mp4") -> str:
    """Gera um caminho único no diretório TEMP_DIR com a extensão especificada."""
    ensure_temp_dir_exists()
    temp_path = os.path.join(TEMP_DIR, f"{uuid4()}.{ext}")
    logger.debug(f"📄 Caminho temporário gerado: {temp_path}")
    return temp_path


# === 💾 Verifica espaço livre (em MB) ===
def get_free_disk_space_mb(path: str = "/") -> float:
    """Retorna o espaço livre no disco (em MB)."""
    try:
        statvfs = os.statvfs(path)
        return round((statvfs.f_frsize * statvfs.f_bavail) / (1024 * 1024), 2)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao verificar espaço em disco: {e}")
        return 0.0


# === 📦 Exportações ===
__all__ = [
    "ensure_temp_dir_exists",
    "remove_dir",
    "remove_file",
    "clear_temp_dir",
    "generate_temp_file_path",
    "get_free_disk_space_mb",
]
