import os
import shutil
import logging
from datetime import datetime
from typing import Optional

# === 🛠️ Logger ===
logger = logging.getLogger("report_backup")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 📁 Diretório de Backup ===
BACKUP_DIR = "backup_reports/"
os.makedirs(BACKUP_DIR, exist_ok=True)
logger.info(f"📁 Diretório de backup de relatórios: {BACKUP_DIR}")

# === 💾 Backup de Relatório ===
def backup_report(file_path: str) -> Optional[str]:
    """Copia um arquivo de relatório para o diretório de backup com um timestamp."""
    if not os.path.isfile(file_path):
        logger.error(f"❌ Arquivo não encontrado para backup: {file_path}")
        return None

    try:
        filename = os.path.basename(file_path)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{timestamp}_{filename}"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        shutil.copy2(file_path, backup_path)
        logger.info(f"✅ Relatório copiado: {backup_filename}")
        return backup_path
    except PermissionError:
        logger.error(f"🔒 Permissão negada ao acessar/copiar: {file_path}")
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao fazer backup de '{file_path}': {e}")
    return None

# === 🧹 Limpeza de Backups Antigos ===
def clean_old_backups(max_backups: int = 5) -> int:
    """Mantém apenas os 'max_backups' mais recentes no diretório de backup."""
    if not os.path.exists(BACKUP_DIR):
        logger.warning(f"⚠️ Diretório de backup não encontrado: {BACKUP_DIR}")
        return 0

    try:
        backup_files = [
            f for f in os.listdir(BACKUP_DIR)
            if os.path.isfile(os.path.join(BACKUP_DIR, f))
        ]
        backup_files.sort(key=lambda f: os.path.getmtime(os.path.join(BACKUP_DIR, f)), reverse=True)

        excess_files = backup_files[max_backups:]
        deleted = 0

        for file in excess_files:
            path = os.path.join(BACKUP_DIR, file)
            os.remove(path)
            logger.info(f"🗑️ Backup removido: {file}")
            deleted += 1

        logger.info(f"🔁 Limpeza concluída: {deleted} arquivos removidos.")
        return deleted

    except Exception as e:
        logger.error(f"❌ Erro durante limpeza de backups: {e}")
        return 0

# === 🧪 Exemplo de Uso ===
if __name__ == "__main__":
    temp_path = "temp_report.txt"
    with open(temp_path, "w") as f:
        f.write("Este é um relatório de teste.\n")

    result = backup_report(temp_path)
    if result:
        print(f"✔️ Backup salvo em: {result}")

    removed = clean_old_backups(max_backups=2)
    print(f"🧹 Total removido: {removed}")

    os.remove(temp_path)
