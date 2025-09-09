import os
import shutil
import logging
import threading
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User, UserRole
from api.deps import get_current_user, require_role

# === ⚙️ Configuração e paths ===
router = APIRouter()

PROCESSED_VIDEOS_DIR = os.getenv("PROCESSED_VIDEOS_DIR", "processed_videos")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backup")
LOG_FILE = os.getenv("BACKUP_LOG_FILE", "logs/backup_restore.log")
BACKUP_INTERVAL_SECONDS = int(os.getenv("BACKUP_INTERVAL_SECONDS", 86400))  # 24h

os.makedirs(PROCESSED_VIDEOS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# === 📝 Logger ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === 📦 Criar backup ===
def create_backup() -> dict:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)

        copied_files = 0
        for file in os.listdir(PROCESSED_VIDEOS_DIR):
            src = os.path.join(PROCESSED_VIDEOS_DIR, file)
            dst = os.path.join(backup_path, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                copied_files += 1

        logging.info(f"✅ Backup criado: {backup_path}, {copied_files} arquivos.")
        return {
            "message": "✅ Backup criado com sucesso",
            "backup_path": backup_path,
            "files_copied": copied_files
        }

    except Exception as e:
        logging.error(f"❌ Erro ao criar backup: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar backup.")

# === ♻️ Restaurar backup ===
def restore_backup(backup_folder: str) -> dict:
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_folder)
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail="Backup não encontrado.")

        restored_files = 0
        for file in os.listdir(backup_path):
            src = os.path.join(backup_path, file)
            dst = os.path.join(PROCESSED_VIDEOS_DIR, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                restored_files += 1

        logging.info(f"✅ Backup restaurado: {backup_folder}, {restored_files} arquivos.")
        return {
            "message": "♻️ Backup restaurado com sucesso",
            "files_restored": restored_files
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"❌ Erro ao restaurar backup: {e}")
        raise HTTPException(status_code=500, detail="Erro ao restaurar backup.")

# === ⏰ Agendador de backup automático ===
def schedule_backup():
    while True:
        time.sleep(BACKUP_INTERVAL_SECONDS)
        try:
            create_backup()
        except Exception as e:
            logging.error(f"❌ Backup automático falhou: {e}")

threading.Thread(target=schedule_backup, daemon=True, name="BackupScheduler").start()

# === 🌐 Endpoints ===

@router.post("/backup", tags=["Admin"], dependencies=[Depends(require_role(UserRole.ADMIN))])
def trigger_backup(current_user: User = Depends(get_current_user)) -> dict:
    """🔄 Gera manualmente um novo backup."""
    return create_backup()

@router.post("/restore/{backup_folder}", tags=["Admin"], dependencies=[Depends(require_role(UserRole.ADMIN))])
def trigger_restore(backup_folder: str, current_user: User = Depends(get_current_user)) -> dict:
    """♻️ Restaura um backup específico por nome da pasta."""
    return restore_backup(backup_folder)

@router.get("/list-backups", tags=["Admin"], dependencies=[Depends(require_role(UserRole.ADMIN))])
def list_backups(current_user: User = Depends(get_current_user)) -> dict:
    """📂 Lista todos os backups disponíveis no sistema."""
    try:
        backups = sorted(os.listdir(BACKUP_DIR), reverse=True)
        return {"backups": backups}
    except Exception as e:
        logging.error(f"❌ Erro ao listar backups: {e}")
        raise HTTPException(status_code=500, detail="Erro ao listar backups.")
