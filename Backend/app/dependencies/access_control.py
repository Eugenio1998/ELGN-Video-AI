# 📁 app/dependencies/access_control.py

import logging
from fastapi import Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

# 📌 Conta de testes (admin liberado por email)
ADMIN_EMAIL = "elgn@tech.com"

# === 🔒 Requer plano pago (Pro, Premium, Empresarial) ===
def require_paid_plan(user: User = Depends(get_current_user)) -> User:
    if user.email == ADMIN_EMAIL or user.role == UserRole.ADMIN:
        return user  # 🔓 Libera admins independente do plano
    if not user.plan or user.plan.name.lower() in ("basic", "basic anual"):
        logger.warning(f"[Access Denied] Plano gratuito: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="🔒 Este recurso está disponível apenas para planos pagos."
        )
    return user

# === ✨ Requer plano Premium ou Empresarial ===
def require_premium_plan(user: User = Depends(get_current_user)) -> User:
    if user.email == ADMIN_EMAIL or user.role == UserRole.ADMIN:
        return user
    allowed = ("premium", "premium anual", "empresarial", "empresarial anual")
    if not user.plan or user.plan.name.lower() not in allowed:
        logger.warning(f"[Access Denied] Plano insuficiente: {user.username} ({user.plan.name if user.plan else 'Nenhum'})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="✨ Este recurso é exclusivo para usuários Premium ou Empresarial."
        )
    return user

# === 🛡️ Requer função ADMIN ===
def require_admin_role(user: User = Depends(get_current_user)) -> User:
    if user.email == ADMIN_EMAIL or user.role == UserRole.ADMIN:
        return user
    logger.warning(f"[Access Denied] Sem permissão de admin: {user.username}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="🔐 Acesso restrito para administradores."
    )

# === 🟢 Requer assinatura ativa ===
def require_active_subscription(user: User = Depends(get_current_user)) -> User:
    if user.email == ADMIN_EMAIL or user.role == UserRole.ADMIN:
        return user
    if not user.subscription or user.subscription.status.lower() != "active":
        logger.warning(f"[Access Denied] Assinatura inativa: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="⚠️ Assinatura inativa ou expirada."
        )
    return user

# === 🟣 Requer plano gratuito (Free) ===
def require_free_plan(user: User = Depends(get_current_user)) -> User:
    if user.email == ADMIN_EMAIL or user.role == UserRole.ADMIN:
        return user
    if not user.plan or user.plan.name.lower() != "free":
        logger.warning(f"[Access Denied] Não é free: {user.username} ({user.plan.name if user.plan else 'Nenhum'})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="🔐 Este recurso é exclusivo para usuários do plano gratuito."
        )
    return user
