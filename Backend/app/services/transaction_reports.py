# 📁 backend/app/services/transaction_reports.py

import csv
import os
import logging
from datetime import datetime
from tempfile import NamedTemporaryFile
from fastapi import Response
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.models.user import User

# === 🛠️ Logger ===
logger = logging.getLogger("transaction_reports")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === 📊 Relatório de Transações ===
def generate_transaction_report_csv(db: Session) -> str:
    """Gera um relatório CSV com todas as assinaturas."""
    logger.info("📊 Iniciando geração de relatório de transações...")
    transactions = db.query(Subscription).all()
    logger.info(f"🔢 Total de transações encontradas: {len(transactions)}")

    try:
        with NamedTemporaryFile(mode="w+", newline='', delete=False, encoding="utf-8-sig") as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(["ID Usuário", "Plano", "Status Pagamento", "Último Pagamento", "Criado em", "Expiração Trial"])
            for t in transactions:
                writer.writerow([
                    t.user_id,
                    t.plan,
                    str(getattr(t, "payment_status", "indefinido")),
                    str(getattr(t, "last_payment_date", "N/A")),
                    str(getattr(t, "created_at", "N/A")),
                    str(getattr(t, "trial_expiration", "N/A")),
                ])
            return temp_file.name
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório de transações: {e}")
        return ""

# === 👤 Relatório de Usuários ===
def generate_user_activity_report_csv(db: Session) -> str:
    """Gera um relatório CSV com informações de atividade de usuários."""
    logger.info("👥 Iniciando geração de relatório de usuários...")
    users = db.query(User).all()
    logger.info(f"🔢 Total de usuários encontrados: {len(users)}")

    try:
        with NamedTemporaryFile(mode="w+", newline='', delete=False, encoding="utf-8-sig") as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(["ID Usuário", "Username", "E-mail", "Criado em", "Ativo", "Verificado"])
            for u in users:
                writer.writerow([
                    u.id,
                    u.username,
                    u.email,
                    str(getattr(u, "created_at", "N/A")),
                    str(getattr(u, "is_active", False)),
                    str(getattr(u, "is_verified", False)),
                ])
            return temp_file.name
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório de usuários: {e}")
        return ""

# === 📅 Relatório por Período ===
def generate_transactions_by_period_csv(db: Session, start_date: datetime = None, end_date: datetime = None) -> str:
    """Gera um relatório CSV de transações entre datas especificadas."""
    logger.info(f"📆 Geração de transações de {start_date} até {end_date}")
    query = db.query(Subscription)
    if start_date:
        query = query.filter(Subscription.created_at >= start_date)
    if end_date:
        query = query.filter(Subscription.created_at <= end_date)

    transactions = query.all()
    logger.info(f"🔎 Transações filtradas: {len(transactions)}")

    try:
        with NamedTemporaryFile(mode="w+", newline='', delete=False, encoding="utf-8-sig") as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(["ID Usuário", "Plano", "Status Pagamento", "Último Pagamento", "Criado em", "Expiração Trial"])
            for t in transactions:
                writer.writerow([
                    t.user_id,
                    t.plan,
                    str(getattr(t, "payment_status", "indefinido")),
                    str(getattr(t, "last_payment_date", "N/A")),
                    str(getattr(t, "created_at", "N/A")),
                    str(getattr(t, "trial_expiration", "N/A")),
                ])
            return temp_file.name
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório por período: {e}")
        return ""

# === 🧹 Remover Arquivo Temporário ===
def cleanup_report_file(file_path: str) -> None:
    """Remove um arquivo de relatório temporário."""
    try:
        os.remove(file_path)
        logger.info(f"🧼 Arquivo removido: {file_path}")
    except FileNotFoundError:
        logger.warning(f"⚠️ Arquivo não encontrado: {file_path}")
    except Exception as e:
        logger.error(f"❌ Erro ao remover arquivo {file_path}: {e}")

# === 📤 Criar Resposta para Download ===
def create_csv_download_response(file_path: str, filename: str) -> Response:
    """Cria uma resposta HTTP para download do CSV."""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
        response = Response(content=content, media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        logger.info(f"📥 Resposta de download criada: {filename}")
        return response
    except FileNotFoundError:
        logger.error(f"❌ Arquivo não encontrado: {file_path}")
        return Response(status_code=404, content="Arquivo não encontrado")
    except Exception as e:
        logger.error(f"❌ Erro ao criar resposta de download: {e}")
        return Response(status_code=500, content="Erro ao gerar o download")
