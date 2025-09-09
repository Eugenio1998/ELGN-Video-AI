# 📂 backend/app/main_log_scheduler.py

import time
import logging
import schedule
from datetime import datetime
from app.config import settings
from app.services.log_backup import backup_logs

# === 🛠️ Logger Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

logger.info("⏳ Iniciando agendador de backup de logs...")

# === 🔁 Função segura de backup ===
def safe_backup():
    try:
        logger.info("📦 Executando backup de logs...")
        backup_logs()
        logger.info("✅ Backup concluído com sucesso.")
    except Exception as e:
        logger.error(f"❌ Erro ao executar backup de logs: {e}")

# === ⏰ Agendamento do backup ===
interval = getattr(settings, "check_interval_hours", 24)

if isinstance(interval, (int, float)) and interval > 0:
    logger.info(f"🔁 Intervalo de verificação definido para {interval} horas.")
    schedule.every(interval).hours.do(safe_backup)
else:
    logger.warning("⚠️ Intervalo inválido. Usando valor padrão de 24 horas.")
    schedule.every(24).hours.do(safe_backup)

# === 🚀 Loop do agendador ===
try:
    while True:
        schedule.run_pending()
        time.sleep(60)
except KeyboardInterrupt:
    logger.warning("🛑 Scheduler interrompido manualmente.")
