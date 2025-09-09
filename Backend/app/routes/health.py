from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from typing import Dict, Any
import time
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn")

@router.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)) -> JSONResponse:
    """
    🔎 Verifica o status de saúde da aplicação e do banco de dados.

    Retorna:
        - status: 'ok' ou 'error'
        - database: 'ok' ou erro específico
        - latency: tempo da resposta da consulta ao banco
    """
    start_time = time.time()

    try:
        db.execute(text("SELECT 1"))
        latency = round(time.time() - start_time, 4)

        logger.info("✅ Health check: banco de dados conectado.")
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "database": "ok",
                "latency": f"{latency}s"
            }
        )

    except Exception as e:
        logger.error(f"❌ Health check falhou: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "database": str(e),
                "latency": None
            }
        )
