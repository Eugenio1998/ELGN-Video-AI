import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, Query, Depends
from api.deps import require_role
from app.models.user import UserRole
from app.services.subscription import redis_client, cancel_subscription, send_email

# === ⚙️ Setup e caminhos ===
router = APIRouter()

VIDEO_DIRS = {
    "completed": "processed_videos/",
    "failed": "failed_videos/",
    "queued": "queued_videos/",
    "processing": "processing_videos/"
}

# Garante que todos os diretórios existam
for path in VIDEO_DIRS.values():
    os.makedirs(path, exist_ok=True)

# === 📁 Função auxiliar ===
def get_video_list(directory: str, status: str, search: Optional[str] = None) -> List[Dict[str, str]]:
    if not os.path.exists(directory):
        return []

    videos = [{"id": f, "name": f, "status": status} for f in os.listdir(directory)]
    if search:
        videos = [v for v in videos if search.lower() in v["name"].lower()]
    return videos

# === 🔍 Listar vídeos ===
@router.get("/admin/videos", dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_all_videos(
    page: int = Query(1, ge=1, description="Página de resultados"),
    limit: int = Query(10, le=100, description="Quantidade de vídeos por página"),
    search: Optional[str] = Query(None, description="Filtrar por nome")
) -> Dict[str, Any]:
    """
    📂 Lista vídeos em diferentes estados: processados, falhados, em fila e em processamento.
    """
    all_videos = []
    for status, path in VIDEO_DIRS.items():
        all_videos += get_video_list(path, status, search)

    start = (page - 1) * limit
    end = start + limit
    return {"videos": all_videos[start:end], "total": len(all_videos)}

# === 🗑️ Deletar vídeo com erro ===
@router.delete("/admin/videos/{video_id}", dependencies=[Depends(require_role(UserRole.ADMIN))])
def delete_video(video_id: str) -> Dict[str, str]:
    file_path = os.path.join(VIDEO_DIRS["failed"], video_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")
    os.remove(file_path)
    return {"message": "✅ Vídeo excluído com sucesso"}

# === ♻️ Reprocessar vídeo ===
@router.post("/admin/reprocess/{video_id}", dependencies=[Depends(require_role(UserRole.ADMIN))])
def reprocess_video(video_id: str) -> Dict[str, str]:
    """
    🔁 Move um vídeo com erro para a fila de reprocessamento.
    """
    source = os.path.join(VIDEO_DIRS["failed"], video_id)
    destination = os.path.join(VIDEO_DIRS["queued"], video_id)

    if not os.path.exists(source):
        raise HTTPException(status_code=404, detail="Vídeo não encontrado")

    os.rename(source, destination)
    return {"message": "🔁 Vídeo enviado para reprocessamento"}

# === 📋 Listar assinaturas no Redis ===
@router.get("/admin/subscriptions", dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_all_subscriptions() -> Dict[str, Any]:
    """
    🔑 Lista assinaturas premium armazenadas no Redis.
    """
    keys = redis_client.keys("subscription:*")
    subscriptions = []

    for key in keys:
        user_id = key.split(":")[1]
        plan = redis_client.get(key)
        expiration = redis_client.get(f"subscription_expiration:{user_id}")
        subscriptions.append({"user_id": user_id, "plan": plan, "expiration": expiration})

    return {"subscriptions": subscriptions}

# === ❌ Cancelar assinatura manualmente ===
@router.post("/admin/cancel/{user_id}", dependencies=[Depends(require_role(UserRole.ADMIN))])
def admin_cancel_subscription(user_id: str, user_email: str) -> Dict[str, str]:
    try:
        message = cancel_subscription(user_id, user_email)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# === 📧 Enviar lembretes de renovação ===
@router.post("/admin/send-renewal-reminders", dependencies=[Depends(require_role(UserRole.ADMIN))])
def send_renewal_reminders() -> Dict[str, List[str]]:
    """
    📬 Envia lembretes de renovação de assinatura premium com vencimento em 3 dias.
    """
    today = datetime.utcnow().date()
    reminders_sent = []

    for key in redis_client.keys("subscription:*"):
        user_id = key.split(":")[1]
        plan = redis_client.get(key)
        expiration_str = redis_client.get(f"subscription_expiration:{user_id}")

        if plan == "premium" and expiration_str:
            try:
                expiration = datetime.strptime(expiration_str, "%Y-%m-%d").date()
                if (expiration - today).days == 3:
                    email = f"user{user_id}@example.com"  # ⚠️ Substituir com consulta real ao banco
                    subject = "Lembrete: sua assinatura premium expira em 3 dias"
                    message = f"Olá! Sua assinatura premium expira em {expiration_str}. Renove para continuar aproveitando os benefícios."
                    send_email(email, subject, message)
                    reminders_sent.append(email)
            except Exception:
                continue

    return {"reminders_sent": reminders_sent}
