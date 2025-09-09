from fastapi import APIRouter, Response, Query, HTTPException, Depends
import redis
import pdfkit
import io
import os
import csv
import json
import logging
import pandas as pd
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from fpdf import FPDF
from typing import Literal

from app.auth.dependencies import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter(tags=["Admin"])

# === 🔧 Configurações e paths ===
PROCESSED_DIR = "processed_videos/"
FAILED_DIR = "failed_videos/"
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

logger = logging.getLogger("reports_logger")
logger.setLevel(logging.INFO)

# === 🔐 Limite de exportações por usuário ===
def check_export_limits(user_id: str):
    key = f"export_limit:{user_id}"
    count = int(redis_client.get(key) or 0)
    if count >= 5:
        logger.warning(f"🚫 Limite de exportações excedido para o usuário {user_id}.")
        raise HTTPException(status_code=429, detail="Limite de exportações excedido. Tente novamente mais tarde.")
    redis_client.setex(key, timedelta(hours=1), count + 1)
    logger.info(f"✅ Exportações atualizadas: {user_id} -> {count + 1}")

# === 📋 Logs no Redis ===
def log_export(report_type: str, user_id: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"{ts} - User ID: {user_id} exportou relatório de {report_type}"
    redis_client.lpush("export_logs", entry)
    logger.info(entry)

def log_payment(user_id: str, amount: float, status: str, transaction_id: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"{ts} - User ID: {user_id} - Pagamento {status.upper()} de {amount} USD - Transação: {transaction_id}"
    redis_client.lpush("payment_logs", entry)
    logger.info(entry)

def log_notification(user_id: str, message: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"{ts} - User ID: {user_id} - Notificação: {message}"
    redis_client.lpush("notification_logs", entry)
    logger.info(entry)

# === 📊 Geração de dados para relatórios ===
def generate_report_data(days: int):
    today = datetime.now()
    start_date = today - pd.to_timedelta(days, unit="D")
    history, total, processed, failed = [], 0, 0, 0

    for folder, status in [(PROCESSED_DIR, "completed"), (FAILED_DIR, "failed")]:
        if not os.path.exists(folder):
            logger.warning(f"⚠️ Diretório não encontrado: {folder}")
            continue

        for file in os.listdir(folder):
            try:
                ctime = datetime.fromtimestamp(os.path.getctime(os.path.join(folder, file)))
                if ctime >= start_date:
                    total += 1
                    if status == "completed":
                        processed += 1
                    else:
                        failed += 1
                    history.append({
                        "date": ctime.strftime("%Y-%m-%d"),
                        "total": total,
                        "processed": processed,
                        "failed": failed,
                        "success_rate": round((processed / total) * 100, 2) if total else 0,
                        "failure_rate": round((failed / total) * 100, 2) if total else 0,
                    })
            except Exception as e:
                logger.error(f"Erro ao processar arquivo '{file}': {e}")

    return {"history": history}

# === 📤 Exportações CSV / PDF ===
@router.get("/admin/export/csv", dependencies=[Depends(require_role(UserRole.ADMIN))])
def export_csv(days: int = Query(7, ge=1, le=90), current_user: User = Depends(get_current_user)):
    report = generate_report_data(days)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data", "Total", "Processados", "Falhas", "Sucesso (%)", "Falha (%)"])
    for row in report["history"]:
        writer.writerow([row[k] for k in ["date", "total", "processed", "failed", "success_rate", "failure_rate"]])
    log_export(f"relatório de processamento CSV ({days} dias)", current_user.id)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=relatorio_{days}_dias.csv"}
    )

@router.get("/admin/export/pdf", dependencies=[Depends(require_role(UserRole.ADMIN))])
def export_pdf(days: int = Query(7, ge=1, le=90), current_user: User = Depends(get_current_user)):
    report = generate_report_data(days)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Relatório de Processamento", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    for row in report["history"]:
        pdf.cell(200, 10, f"{row['date']} | Total: {row['total']} | OK: {row['processed']} | Erros: {row['failed']}", ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    log_export(f"relatório de processamento PDF ({days} dias)", current_user.id)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=relatorio_{days}_dias.pdf"}
    )

# === 📦 Exportar Assinaturas ===
@router.get("/admin/reports/subscriptions/csv", dependencies=[Depends(require_role(UserRole.ADMIN))])
def export_subscriptions_csv(plan: str = Query(None), current_user: User = Depends(get_current_user)):
    check_export_limits(current_user.id)
    keys = redis_client.keys("subscription:*")
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["User ID", "Plano", "Expira em"])
    for key in keys:
        uid = key.split(":")[1]
        plan_ = redis_client.get(key)
        expiration = redis_client.get(f"subscription_expiration:{uid}") or "-"
        if plan and plan_ != plan:
            continue
        writer.writerow([uid, plan_, expiration])
    log_export("assinaturas CSV", current_user.id)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=assinaturas.csv"}
    )

@router.get("/admin/reports/subscriptions/pdf", dependencies=[Depends(require_role(UserRole.ADMIN))])
def export_subscriptions_pdf(plan: str = Query(None), current_user: User = Depends(get_current_user)):
    check_export_limits(current_user.id)
    keys = redis_client.keys("subscription:*")
    html = """
    <html><head><title>Assinaturas</title></head><body>
    <h2>Relatório de Assinaturas</h2><table border='1'>
    <tr><th>User ID</th><th>Plano</th><th>Expira em</th></tr>
    """
    for key in keys:
        uid = key.split(":")[1]
        plan_ = redis_client.get(key)
        expiration = redis_client.get(f"subscription_expiration:{uid}") or "-"
        if plan and plan_ != plan:
            continue
        html += f"<tr><td>{uid}</td><td>{plan_}</td><td>{expiration}</td></tr>"
    html += "</table></body></html>"

    try:
        pdf = pdfkit.from_string(html, False)
        log_export("assinaturas PDF", current_user.id)
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=assinaturas.pdf"}
        )
    except Exception as e:
        logger.error(f"Erro ao gerar PDF de assinaturas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar relatório.")

# === 🧾 Logs do sistema
@router.get("/admin/reports/logs", dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_export_logs(current_user: User = Depends(get_current_user)):
    return {"logs": redis_client.lrange("export_logs", 0, 50)}

@router.get("/admin/reports/payments/logs", dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_payment_logs(current_user: User = Depends(get_current_user)):
    return {"logs": redis_client.lrange("payment_logs", 0, 50)}

@router.get("/admin/reports/notifications/logs", dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_notification_logs(current_user: User = Depends(get_current_user)):
    return {"logs": redis_client.lrange("notification_logs", 0, 50)}
