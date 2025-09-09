import logging
from typing import Dict, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models.user import User, UserRole
from app.routes.push_cleanup import validate_and_clean_push_subscriptions

router = APIRouter(tags=["Admin"])
logger = logging.getLogger(__name__)

@router.post(
    "/admin/push/cleanup",
    response_model=Dict[str, Union[int, str]],
    dependencies=[Depends(require_role(UserRole.ADMIN))]
)
def manual_push_cleanup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🧹 Limpeza manual de inscrições inválidas de notificações push.
    Apenas para administradores.
    """
    logger.info(f"🛠️ Admin '{current_user.username}' acionou limpeza manual de push notifications.")

    try:
        result = validate_and_clean_push_subscriptions(db)

        logger.info(
            f"✅ Push cleanup concluída — Removidas: {result['removed']} / Verificadas: {result['total_checked']}"
        )

        return {
            "message": "Limpeza de inscrições push concluída com sucesso.",
            "removed": result["removed"],
            "total_checked": result["total_checked"],
        }

    except Exception as e:
        logger.exception("❌ Erro ao executar a limpeza de notificações push.")
        raise HTTPException(status_code=500, detail="Erro ao executar a limpeza.")
