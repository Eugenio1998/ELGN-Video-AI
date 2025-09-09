# 📁 backend/app/routes/security.py

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User, UserRole

import redis
import json
import os
import csv
import smtplib
import logging
from io import StringIO
from email.message import EmailMessage
from email.utils import formataddr

# === 📌 Configuração ===
router = APIRouter(tags=["Segurança"])
logger = logging.getLogger("security")
logger.setLevel(logging.INFO)

# 🔐 Redis
redis_conn = redis.Redis(host="localhost", port=6379, db=4, decode_responses=True)

# 📬 E-mail
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
ADMIN_EMAILS = [e.strip() for e in os.getenv("ADMIN_EMAILS", "admin@elgn.ai").split(",") if e.strip()]

EMAIL_CONFIG_OK = all([EMAIL_HOST, EMAIL_USER, EMAIL_PASS, ADMIN_EMAILS])
if not EMAIL_CONFIG_OK:
    logger.warning("⚠️ Configurações de e-mail incompletas. Alertas de segurança não serão enviados por e-mail.")

# === ⏱️ Controle de alertas repetidos por IP ===
def is_recent_alert(ip: str, minutes: int = 5) -> bool:
    key = f"suspicious:alert:{ip}"
    if redis_conn.exists(key):
        return True
    redis_conn.setex(key, timedelta(minutes=minutes), "sent")
    return False

# === 🚨 Loga tentativa suspeita e tenta enviar e-mail ===
def log_suspicious_activity(username: str, ip: str, reason: str):
    log_data = {
        "username": username,
        "ip": ip,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reason": reason
    }

    try:
        redis_conn.rpush("suspicious_activities", json.dumps(log_data))
        logger.warning(f"🚨 Atividade suspeita registrada: {log_data}")

        if not is_recent_alert(ip):
            send_security_alert(log_data)
        else:
            logger.info(f"⏳ Alerta já enviado recentemente para IP {ip}. Ignorando novo envio.")
    except Exception as e:
        logger.error(f"❌ Falha ao registrar atividade suspeita: {e}")

# === 📬 Envia e-mail de alerta de segurança ===
def send_security_alert(log_data: dict):
    if not EMAIL_CONFIG_OK:
        logger.warning("📧 Configuração de e-mail incompleta. Alerta não enviado.")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = "🚨 Alerta de Segurança: Atividade Suspeita"
        msg["From"] = formataddr(("ELGN.AI Segurança", EMAIL_USER))
        msg["To"] = ", ".join(ADMIN_EMAILS)
        msg.set_content(
            f"🔍 Atividade suspeita detectada:\n\n"
            f"Usuário: {log_data['username']}\n"
            f"Endereço IP: {log_data['ip']}\n"
            f"Motivo: {log_data['reason']}\n"
            f"Data/Hora: {log_data['timestamp']}\n\n"
            f"Verifique o painel administrativo."
        )

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        logger.info(f"📨 Alerta de segurança enviado para: {', '.join(ADMIN_EMAILS)}")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar e-mail de alerta: {e}")

# === 🔎 Listar atividades suspeitas (últimos 50) ===
@router.get("/suspicious-activities", dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_suspicious_activities(current_user: User = Depends(get_current_user)):
    try:
        logs = redis_conn.lrange("suspicious_activities", -50, -1)
        return {"suspicious_activities": [json.loads(l) for l in logs]}
    except Exception as e:
        logger.error(f"❌ Erro ao buscar logs: {e}")
        raise HTTPException(status_code=500, detail="Erro ao acessar atividades suspeitas.")

# === 📥 Exportar atividades suspeitas em CSV ===
@router.get("/suspicious-activities/export", dependencies=[Depends(require_role(UserRole.ADMIN))])
def export_suspicious_activities(current_user: User = Depends(get_current_user)):
    try:
        logs = redis_conn.lrange("suspicious_activities", 0, -1)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Username", "IP", "Timestamp", "Reason"])
        for l in logs:
            d = json.loads(l)
            writer.writerow([d["username"], d["ip"], d["timestamp"], d["reason"]])
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=suspicious_activities.csv"}
        )
    except Exception as e:
        logger.error(f"❌ Erro ao exportar logs: {e}")
        raise HTTPException(status_code=500, detail="Erro ao exportar atividades.")
