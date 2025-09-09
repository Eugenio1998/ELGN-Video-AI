from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User, UserRole

from datetime import datetime
from fpdf import FPDF
import schedule
import threading
import smtplib
import shutil
import logging
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# === ⚙️ Inicialização ===
router = APIRouter(tags=["Métricas do Sistema"])
load_dotenv()

# === 📁 Configurações ===
LOG_FILE = "logs/system_metrics.log"
BACKUP_DIR = "backup_reports"
PDF_LINE_LIMIT = int(os.getenv("PDF_LINE_LIMIT", 50))
os.makedirs(BACKUP_DIR, exist_ok=True)

# === 🛠️ Logger ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("system_metrics")

# === 📧 Configurações de E-mail ===
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# === 📄 Geração de PDF ===
def generate_pdf_report() -> str | None:
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "📊 Relatório de Métricas do Servidor", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=11)

        with open(LOG_FILE, "r", encoding="utf-8") as log:
            lines = log.readlines()[-PDF_LINE_LIMIT:]
            for line in lines:
                pdf.multi_cell(0, 10, line.strip())

        filename = f"system_metrics_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
        filepath = os.path.join(BACKUP_DIR, filename)
        pdf.output(filepath)
        logger.info(f"✅ PDF gerado com sucesso: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"❌ Erro ao gerar PDF: {e}")
        return None

# === 💾 Backup de Relatório ===
def backup_report():
    logger.info("⏳ Iniciando processo de backup de relatório...")
    pdf_file = generate_pdf_report()
    if pdf_file:
        logger.info(f"🗃️ Backup armazenado: {pdf_file}")
    else:
        logger.warning("⚠️ Backup falhou: arquivo PDF não foi gerado.")

# === 📤 Envio por E-mail ===
def send_report_email():
    logger.info("📡 Iniciando envio de relatório por e-mail...")

    if not EMAIL_SENDER or not EMAIL_RECEIVER:
        logger.error("❌ EMAIL_SENDER ou EMAIL_RECEIVER não configurados.")
        return

    pdf_file = generate_pdf_report()
    if not pdf_file:
        logger.warning("⚠️ Nenhum PDF gerado para envio.")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = "📊 Relatório de Métricas do Servidor"
        msg.attach(MIMEText("Segue em anexo o relatório mais recente de métricas do sistema.", "plain"))

        with open(pdf_file, "rb") as file:
            part = MIMEApplication(file.read(), Name=os.path.basename(pdf_file))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(pdf_file)}"'
            msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        logger.info(f"📬 Relatório enviado com sucesso para {EMAIL_RECEIVER}.")

    except smtplib.SMTPException as smtp_ex:
        logger.error(f"❌ Erro SMTP: {smtp_ex}")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar e-mail: {e}")

# === ⏰ Agendador ===
schedule.every().day.at("08:00").do(send_report_email)
schedule.every().day.at("08:05").do(backup_report)

def run_scheduler():
    logger.info("📆 Agendador iniciado em thread separada.")
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logger.error(f"⛔ Erro no agendador: {e}")

threading.Thread(target=run_scheduler, daemon=True, name="SchedulerThread").start()

# === 📡 Endpoints protegidos (admin) ===
@router.get("/metrics/send-report", dependencies=[Depends(require_role(UserRole.ADMIN))])
def trigger_email(current_user: User = Depends(get_current_user)):
    """📤 Dispara envio de relatório por e-mail (admin)."""
    try:
        send_report_email()
        logger.info(f"🔔 Envio manual acionado por {current_user.username}.")
        return {"message": "Relatório enviado com sucesso."}
    except Exception as e:
        logger.error(f"❌ Erro no envio manual por {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar relatório: {e}")

@router.get("/metrics/backup-report", dependencies=[Depends(require_role(UserRole.ADMIN))])
def trigger_backup(current_user: User = Depends(get_current_user)):
    """💾 Dispara backup de relatório (admin)."""
    try:
        backup_report()
        logger.info(f"📂 Backup manual acionado por {current_user.username}.")
        return {"message": "Backup concluído com sucesso."}
    except Exception as e:
        logger.error(f"❌ Erro no backup manual por {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no backup: {e}")
