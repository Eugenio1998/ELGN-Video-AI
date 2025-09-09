import os
import io
import csv
import redis
import logging
from fastapi import APIRouter, Response, Query, HTTPException
from datetime import datetime
from typing import Literal, Dict, Any

from app.services.redis_cache import cache_get, cache_set, cache_ttl

router = APIRouter()
logger = logging.getLogger("uvicorn")

# 🔧 Conexão Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True
)

# 🔐 Tipos de logs suportados
LOG_TYPES: dict[Literal["uploads", "deletions", "notifications"], str] = {
    "uploads": "upload_logs",
    "deletions": "delete_logs",
    "notifications": "notification_logs"
}

# ===================== 🔍 LOGS COM FILTRO =====================
@router.get("/logs/{log_type}", tags=["Logs"])
def get_logs_filtered(
    log_type: Literal["uploads", "deletions", "notifications"],
    limit: int = Query(50, ge=1, le=500),
    search: str = Query(None),
    sort_desc: bool = Query(True)
) -> Dict[str, Any]:
    """
    🔍 Obtém logs com filtros opcionais (busca, ordenação).
    """
    try:
        redis_key = LOG_TYPES[log_type]
        logs = redis_client.lrange(redis_key, 0, limit)

        if search:
            logs = [log for log in logs if search.lower() in log.lower()]
        if sort_desc:
            logs.reverse()

        return {"logs": logs, "total": len(logs)}

    except Exception as e:
        logger.error(f"❌ Erro ao buscar logs filtrados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar logs.")


# ===================== 📤 EXPORTAÇÃO CSV =====================
@router.get("/logs/{log_type}/export", tags=["Logs"])
def export_logs_csv(
    log_type: Literal["uploads", "deletions", "notifications"],
    limit: int = Query(100, ge=1, le=1000)
) -> Response:
    """
    📤 Exporta logs para CSV.
    """
    try:
        redis_key = LOG_TYPES[log_type]
        logs = redis_client.lrange(redis_key, 0, limit)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "Ação", "Detalhes"])

        for log in logs:
            parts = log.split(" - ")
            if len(parts) == 3:
                writer.writerow(parts)
            else:
                writer.writerow([datetime.utcnow().isoformat(), "desconhecido", log])

        csv_data = output.getvalue()
        response = Response(content=csv_data, media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={log_type}_logs.csv"
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Content-Encoding"] = "utf-8"
        return response

    except Exception as e:
        logger.error(f"❌ Erro ao exportar logs para CSV: {e}")
        raise HTTPException(status_code=500, detail="Erro ao exportar logs.")


# ===================== 📦 CACHE LOGS =====================
@router.get("/admin/logs/cache", tags=["Admin"])
def get_logs_cached(
    log_type: Literal["uploads", "deletions", "notifications"] = Query(...)
) -> Dict[str, Any]:
    """
    📦 Retorna logs do cache Redis (fallback para Redis direto).
    """
    try:
        cache_key = f"{log_type}_logs"
        cached_logs = cache_get(cache_key, prefix="logs")

        if cached_logs:
            return {
                "source": "cache",
                "ttl_seconds": cache_ttl(cache_key, prefix="logs"),
                "logs": cached_logs
            }

        redis_key = LOG_TYPES[log_type]
        logs = redis_client.lrange(redis_key, 0, 50)
        cache_set(cache_key, logs, expiration=3600, prefix="logs")

        return {
            "source": "redis",
            "logs": logs
        }

    except Exception as e:
        logger.error(f"❌ Erro ao recuperar cache de logs: {e}")
        raise HTTPException(status_code=500, detail="Erro ao recuperar cache de logs.")


# ===================== 📄 PAGINAÇÃO =====================
@router.get("/admin/logs/paginated", tags=["Admin"])
def get_paginated_logs(
    log_type: Literal["uploads", "deletions", "notifications"],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """
    📄 Paginação de logs no Redis.
    """
    try:
        redis_key = LOG_TYPES[log_type]
        logs = redis_client.lrange(redis_key, offset, offset + limit - 1)
        return {
            "type": log_type,
            "total": len(logs),
            "logs": logs
        }

    except Exception as e:
        logger.error(f"❌ Erro ao paginar logs: {e}")
        raise HTTPException(status_code=500, detail="Erro ao paginar logs.")
