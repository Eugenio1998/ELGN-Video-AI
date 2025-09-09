import os
import time
import signal
import schedule
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.subscription import check_subscription_status

# === 🔧 Configuração ===
load_dotenv()
CHECK_INTERVAL_HOURS = max(1, int(os.getenv("CHECK_INTERVAL_HOURS", 24)))

# === 🛠️ Logger ===
logger = logging.getLogger("schedule_tasks")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 🧾 Tarefa de Verificação ===
def run_subscription_check():
    db: Session = SessionLocal()
    try:
        logger.info("📡 Verificando status das assinaturas...")
        check_subscription_status(db)
        logger.info("✅ Verificação concluída com sucesso.")
    except Exception as e:
        logger.exception("❌ Erro ao verificar assinaturas:", exc_info=e)
    finally:
        db.close()

# === 🧼 Encerramento Seguro ===
def graceful_shutdown(signum, frame):
    logger.info("🔻 Encerrando agendador com segurança...")
    exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

# === 📆 Inicialização Agendador ===
def start_scheduler():
    logger.info(f"⏰ Verificação de assinaturas a cada {CHECK_INTERVAL_HOURS}h.")
    schedule.every(CHECK_INTERVAL_HOURS).hours.do(run_subscription_check)

    logger.info("🚀 Agendador iniciado. Aguardando tarefas futuras...")
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logger.error(f"❌ Erro inesperado no loop de agendamento: {e}")
            time.sleep(60)

# === 🚀 Execução direta ===
if __name__ == "__main__":
    logger.info("🟢 Iniciando sistema de tarefas agendadas...")
    start_scheduler()
