# 📁 app/api/endpoints/auth.py

from fastapi import APIRouter
from app.auth import register, login  # 👈 Importação das subrotas

router = APIRouter()

# 👉 Inclusão das rotas de autenticação agrupadas sob o prefixo /auth
router.include_router(register.router, prefix="/auth", tags=["Auth"])
router.include_router(login.router, prefix="/auth", tags=["Auth"])
