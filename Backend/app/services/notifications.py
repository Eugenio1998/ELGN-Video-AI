import os
import smtplib
import redis
import logging
from datetime import datetime
from dotenv import load_dotenv
from email.mime.text import MIMEText
from typing import List, Optional

# === 🔧 Variáveis de Ambiente ===
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# === 🛠️ Logger ===
logger = logging.getLogger("notifications_service")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 🔌 Redis ===
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("🔔✅ Redis conectado com sucesso.")
except redis.exceptions.ConnectionError as e:
    logger.error(f"🔔❌ Erro ao conectar Redis: {e}")
    redis_client = None

# === 🔑 Utilitário de chave Redis ===
def get_redis_key(user_id: str, date: Optional[str] = None) -> str:
    date_str = date or str(datetime.utcnow().date())
    return f"notifications:{user_id}:{date_str}"

# === 📧 Enviar e-mail ===
def send_email_notification(to_email: str, subject: str, message: str) -> bool:
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASSWORD]):
        logger.error("📨❌ SMTP não configurado corretamente.")
        return False

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        logger.info(f"📤 E-mail enviado para {to_email} com assunto: {subject}")
        store_email_log(to_email, subject, "success")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("🔒 Erro de autenticação SMTP.")
        store_email_log(to_email, subject, "failed: auth error")
    except smtplib.SMTPConnectError:
        logger.error("📡 Falha na conexão SMTP.")
        store_email_log(to_email, subject, "failed: connect error")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar e-mail: {e}")
        store_email_log(to_email, subject, f"failed: {str(e)}")
    return False

# === 🗂️ Armazenar notificação ===
def store_notification(user_id: str, message: str) -> None:
    if not redis_client:
        logger.error("📦❌ Redis não disponível.")
        return

    try:
        key = get_redis_key(user_id)
        redis_client.lpush(key, message)
        redis_client.expire(key, 86400)  # 1 dia
        logger.info(f"📦 Notificação salva para {user_id}")
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao armazenar notificação: {e}")

# === 📬 Listar notificações de hoje ===
def get_user_notifications(user_id: str) -> List[str]:
    if not redis_client:
        return []

    try:
        key = get_redis_key(user_id)
        return redis_client.lrange(key, 0, -1)
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Falha ao buscar notificações: {e}")
        return []

# === 🧾 Log de envio de e-mail ===
def store_email_log(recipient: str, subject: str, status: str) -> None:
    if not redis_client:
        return

    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{timestamp} - Para: {recipient} - Assunto: {subject} - Status: {status}"
        redis_client.rpush("emails:log", entry)
        redis_client.expire("emails:log", 2592000)  # 30 dias
        logger.info(f"📗 Log de e-mail armazenado: {entry}")
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao registrar log de e-mail: {e}")

# === 📅 Notificações por data ===
def get_user_notifications_from_date(user_id: str, date_str: str) -> List[str]:
    if not redis_client:
        return []

    try:
        key = get_redis_key(user_id, date_str)
        return redis_client.lrange(key, 0, -1)
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao buscar notificações: {e}")
        return []

# === 🧽 Limpar notificações ===
def clear_user_notifications(user_id: str, date_str: Optional[str] = None) -> int:
    if not redis_client:
        return 0

    try:
        key = get_redis_key(user_id, date_str)
        deleted = redis_client.delete(key)
        logger.info(f"🗑️ Notificações limpas para {user_id} ({date_str or 'hoje'})")
        return deleted
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Erro ao remover notificações: {e}")
        return 0
