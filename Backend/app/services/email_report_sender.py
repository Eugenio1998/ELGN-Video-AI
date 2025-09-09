# 📧 Envio de E-mails com Relatórios (com ou sem anexo)

import os
import smtplib
import logging
from typing import List, Optional
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# === 🔧 Variáveis de Ambiente ===
load_dotenv()
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_SENDER")
EMAIL_PASS = os.getenv("EMAIL_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@elgn.ai")

# === 🛠️ Logger ===
logger = logging.getLogger("email_report")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 🧱 Criação da Mensagem de E-mail ===
def create_email_message(
    subject: str,
    body: str,
    recipients: List[str],
    file_path: Optional[str] = None
) -> MIMEMultipart:
    """Cria uma mensagem de e-mail com corpo de texto e anexo opcional."""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if file_path:
        try:
            with open(file_path, "rb") as f:
                attachment = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                attachment["Content-Disposition"] = f"attachment; filename={os.path.basename(file_path)}"
                msg.attach(attachment)
            logger.info(f"📎 Anexo adicionado: {file_path}")
        except FileNotFoundError:
            logger.error(f"❌ Arquivo de anexo não encontrado: {file_path}")
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao anexar o arquivo: {e}")
            raise

    return msg

# === 📤 Envio de E-mail com ou sem Anexo ===
def send_report_email(
    file_path: Optional[str],
    subject: str,
    body: str,
    recipients: Optional[List[str]] = None
) -> bool:
    """Envia e-mail com relatório (opcionalmente com anexo)."""
    recipients = recipients or [ADMIN_EMAIL]

    if not EMAIL_USER or not EMAIL_PASS:
        logger.error("⚠️ Credenciais de e-mail ausentes.")
        return False

    try:
        msg = create_email_message(subject, body, recipients, file_path)
    except Exception:
        return False

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        logger.info(f"📤 E-mail enviado com sucesso para: {', '.join(recipients)}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("🔐 Falha de autenticação no servidor SMTP.")
    except smtplib.SMTPConnectError:
        logger.error(f"🔌 Falha na conexão com servidor SMTP {EMAIL_HOST}:{EMAIL_PORT}")
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao enviar e-mail: {e}")
    return False

# === 🧪 Execução Local de Teste ===
if __name__ == "__main__":
    test_file = "test_report.txt"
    with open(test_file, "w") as f:
        f.write("Relatório de Teste - ELGN Video.AI\n")

    success = send_report_email(
        file_path=test_file,
        subject="📊 Relatório de Teste",
        body="Segue o relatório gerado automaticamente pelo sistema."
    )

    print("✅ Enviado!" if success else "❌ Falhou.")
    os.remove(test_file)
