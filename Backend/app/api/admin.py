import os
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import require_role
from app.models.user import User, UserRole
from app.services.transaction_reports import (
    generate_transaction_report_csv,
    generate_user_activity_report_csv
)
from app.api.error_response import ErrorResponse

# === Logger ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# === Router ===
router = APIRouter(prefix="/admin", tags=["Admin Reports"])

# === Utilitário: Streaming de CSV ===
def stream_csv_file(temp_file_path: str, filename: str):
    if not os.path.exists(temp_file_path):
        logger.error(f"❌ Arquivo não encontrado: {temp_file_path}")
        raise HTTPException(status_code=404, detail="Arquivo de relatório não encontrado.")

    return StreamingResponse(
        open(temp_file_path, "rb"),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# === ROTA: Relatório de transações ===
@router.get(
    "/reports/transactions",
    summary="📄 Relatório de transações (CSV)",
    responses={403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def generate_transaction_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Gera e retorna um arquivo CSV com dados de transações.
    Requer permissão de administrador.
    """
    try:
        temp_file_path = generate_transaction_report_csv(db)
        filename = f"transaction_report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
        logger.info(f"📁 [admin:{current_user.id}] Gerou relatório de transações.")
        return stream_csv_file(temp_file_path, filename)
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório de transações: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar o relatório de transações.")

# === ROTA: Relatório de atividade de usuários ===
@router.get(
    "/reports/user-activity",
    summary="🕵️ Relatório de atividades de usuários (CSV)",
    responses={403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def generate_user_activity_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Gera e retorna um arquivo CSV com atividades de usuários.
    Requer permissão de administrador.
    """
    try:
        temp_file_path = generate_user_activity_report_csv(db)
        filename = f"user_activity_report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
        logger.info(f"📁 [admin:{current_user.id}] Gerou relatório de atividades de usuários.")
        return stream_csv_file(temp_file_path, filename)
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório de atividades de usuários: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar o relatório de atividades de usuários.")
