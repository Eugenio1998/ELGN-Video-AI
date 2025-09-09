import os
import logging
from fastapi import APIRouter, Depends, Response, HTTPException, Query
from typing import Optional

from api.deps import require_role
from app.models.user import UserRole
from app.core.config import settings  # ✅ centralização de configs

# === 🔧 Configurações ===
router = APIRouter()
logger = logging.getLogger(__name__)

LOG_FILE_PATH = settings.LOG_FILE or "logs/audit.log"
MAX_LOG_LINES = 1000

# Criação do diretório se não existir
try:
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
except Exception as e:
    logger.warning(f"⚠️ Falha ao criar diretório de logs: {e}")


# === 📄 Acesso aos Logs ===
@router.get("/logs", dependencies=[Depends(require_role(UserRole.ADMIN))], response_class=Response)
def get_logs(
    limit: int = Query(MAX_LOG_LINES, ge=10, le=5000, description="Número de linhas a retornar (padrão: 1000)")
) -> Response:
    """
    📄 Retorna as últimas linhas do log do sistema (audit.log).
    🔒 Acesso restrito a administradores.
    """
    if not os.path.isfile(LOG_FILE_PATH):
        logger.warning("⚠️ Arquivo de log não encontrado.")
        return Response(content="Nenhum log encontrado.", media_type="text/plain")

    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()
            selected_logs = lines[-limit:] if limit < len(lines) else lines
            return Response(content="".join(selected_logs), media_type="text/plain")

    except Exception as e:
        logger.error(f"❌ Erro ao ler o arquivo de log: {e}")
        raise HTTPException(status_code=500, detail="Erro ao acessar os logs do sistema.")
