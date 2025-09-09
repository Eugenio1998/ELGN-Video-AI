# 📁 app/auth/__init__.py

"""
Módulo de autenticação da ELGN Video.AI
Inclui hashing, JWT, autenticação, registro de usuário e utilitários de segurança.
Agrupa todos os routers em um único `auth_router` para incluir no main.py
"""

from fastapi import APIRouter
from . import hashing, jwt, login, register, utils
from .login import router as login_router
from .router import router as router_router

auth_router = APIRouter()
auth_router.include_router(login_router)
auth_router.include_router(router_router)

__all__ = [
    "hashing",
    "jwt",
    "login",
    "register",
    "utils",
    "auth_router",  # agora expõe o router unificado
]
