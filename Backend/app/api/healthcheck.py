import time
import logging
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["Health"])

@router.get("/health", status_code=status.HTTP_200_OK)
def healthcheck(db: Session = Depends(get_db)):
    """
    ✅ Verifica se a aplicação e o banco de dados estão operacionais.
    """
    start_time = time.time()

    # Teste rápido de conexão com o banco
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.warning(f"[❌ DB] Falha na verificação de status: {e}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados.")

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(f"[✅ Healthcheck] OK | DB: {db_status} | Tempo: {duration_ms} ms")

    return {
        "status": "ok",
        "database": db_status,
        "environment": getattr(settings, "ENVIRONMENT", "undefined"),
        "version": getattr(settings, "APP_VERSION", "v1"),
        "uptime_ms": duration_ms
    }
