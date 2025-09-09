# 🧾 Serviço de Backup e Rotação de Logs

import os
import shutil
import logging
from datetime import datetime
from dotenv import load_dotenv

# === 🔧 Variáveis de Ambiente ===
load_dotenv()
LOG_DIR = os.getenv("LOG_DIR", "logs")
BACKUP_DIR = os.getenv("BACKUP_DIR", "logs_backup")
LOG_FILE = os.path.join(LOG_DIR, "audit.log")
CLEAR_LOG_AFTER_BACKUP = os.getenv("CLEAR_LOG_AFTER_BACKUP", "False").lower() == "true"
MAX_BACKUPS = int(os.getenv("MAX_LOG_BACKUPS", 5))

# === 🛠️ Logger ===
logger = logging.getLogger("log_backup")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 📁 Garantir existência dos diretórios ===
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# === 🔎 Listar backups existentes ===
def _list_backups() -> list[str]:
    try:
        return sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.startswith("audit_backup_") and f.endswith(".log")],
            key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)),
            reverse=True
        )
    except Exception as e:
        logger.error(f"❌ Erro ao listar backups: {e}")
        return []

# === 📤 Criar backup do log principal ===
def backup_logs() -> None:
    if not os.path.isfile(LOG_FILE):
        logger.warning(f"⚠️ Log principal não encontrado: {LOG_FILE}")
        return

    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f"audit_backup_{timestamp}.log")

    try:
        shutil.copy2(LOG_FILE, backup_path)
        logger.info(f"✅ Backup criado com sucesso: {backup_path}")

        if CLEAR_LOG_AFTER_BACKUP:
            if os.access(LOG_FILE, os.W_OK):
                with open(LOG_FILE, "w") as f:
                    f.write("")
                logger.info(f"🧹 Log original limpo: {LOG_FILE}")
            else:
                logger.warning(f"🔐 Sem permissão para limpar log: {LOG_FILE}")
    except Exception as e:
        logger.error(f"❌ Erro ao criar backup: {e}")

# === 🧹 Rotacionar backups antigos ===
def rotate_logs(max_backups: int = MAX_BACKUPS) -> None:
    try:
        backups = _list_backups()
        excess = backups[max_backups:]

        for file in excess:
            path = os.path.join(BACKUP_DIR, file)
            try:
                if os.path.isfile(path) and os.access(path, os.W_OK):
                    os.remove(path)
                    logger.info(f"🗑️ Backup removido: {path}")
                else:
                    logger.warning(f"🔐 Sem permissão para remover: {path}")
            except Exception as e:
                logger.error(f"❌ Erro ao remover backup '{path}': {e}")
    except Exception as e:
        logger.error(f"❌ Erro ao rotacionar logs: {e}")

# === 🔄 Gerenciar logs (backup + rotação) ===
def manage_logs() -> None:
    logger.info("🔧 Iniciando gerenciamento de logs...")
    backup_logs()
    rotate_logs()
    logger.info("✅ Gerenciamento de logs finalizado.")

# === 👟 Execução manual (debug/teste local) ===
if __name__ == "__main__":
    manage_logs()
