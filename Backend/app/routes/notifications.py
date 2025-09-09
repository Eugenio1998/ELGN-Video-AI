import io
import csv
import redis
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Response, Query, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from api.deps import get_current_user
from app.models.user import User
from app.services.notifications import (
    store_notification,
    send_email_notification,
    get_notification_history,
    redis_client,
)

router = APIRouter()

# 🎯 Mapeamento dos tipos de log permitidos
LOG_KEYS = {
    "uploads": "upload_logs",
    "deletions": "delete_logs",
    "notifications": "notification_logs"
}


# === 🔐 Validação de tipo de log ===
def get_redis_key(log_type: Literal["uploads", "deletions", "notifications"]) -> str:
    redis_key = LOG_KEYS.get(log_type)
    if not redis_key:
        raise HTTPException(status_code=400, detail="Tipo de log inválido.")
    return redis_key


# === 🔍 Buscar logs com filtros ===
@router.get("/logs/{log_type}", tags=["Logs"])
def get_logs(
    log_type: Literal["uploads", "deletions", "notifications"],
    limit: int = Query(50, ge=1, le=500),
    search: str = Query(None),
    sort_desc: bool = Query(True),
    current_user: User = Depends(get_current_user)
):
    """
    🔍 Busca logs no Redis com filtros de busca e ordenação.
    """
    try:
        redis_key = get_redis_key(log_type)
        logs = redis_client.lrange(redis_key, 0, limit)

        if search:
            logs = [log for log in logs if search.lower() in log.lower()]
        if sort_desc:
            logs.reverse()

        return {"logs": logs, "total": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar logs: {e}")


# === 📤 Exportar logs como CSV ===
@router.get("/logs/{log_type}/export", tags=["Logs"])
def export_logs_csv(
    log_type: Literal["uploads", "deletions", "notifications"],
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """
    📤 Exporta logs para CSV com separação de campos.
    """
    try:
        redis_key = get_redis_key(log_type)
        logs = redis_client.lrange(redis_key, 0, limit)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "Ação", "Detalhes"])

        for log in logs:
            parts = log.split(" - ")
            writer.writerow(parts if len(parts) == 3 else [datetime.utcnow().isoformat(), "desconhecido", log])

        response = Response(content=output.getvalue(), media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={log_type}_logs.csv"
        response.headers["Cache-Control"] = "no-cache"
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar logs: {e}")


# === 🔔 Notificações do dia ===
@router.get("/notifications/{user_id}", tags=["Notifications"])
def get_notifications(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    🔔 Retorna notificações armazenadas no Redis para o dia atual.
    """
    try:
        key = f"notifications:{user_id}:{datetime.today().date()}"
        if not redis_client.exists(key):
            return {"user_id": user_id, "notifications": []}

        notifications = redis_client.lrange(key, 0, -1)
        return {"user_id": user_id, "notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar notificações: {e}")


# === 🗂️ Histórico completo de notificações ===
@router.get("/notifications/history/{user_id}", tags=["Notifications"])
def get_full_notification_history(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    🗂️ Busca histórico completo de notificações salvas.
    """
    try:
        history = get_notification_history(user_id)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {e}")


# === 📬 Enviar notificação para e-mail e Redis ===

class NotificationPayload(BaseModel):
    email: EmailStr
    message: str

@router.post("/notify/{user_id}", tags=["Notifications"])
def notify_user(
    user_id: str,
    payload: NotificationPayload,
    current_user: User = Depends(get_current_user)
):
    """
    📬 Envia notificação para o Redis e para o e-mail do usuário.
    """
    try:
        store_notification(user_id, payload.message)
        send_email_notification(payload.email, "Nova Notificação", payload.message)
        return {"message": "Notificação enviada e armazenada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao notificar usuário: {e}")
