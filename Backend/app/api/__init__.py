# 📦 Inicializador do pacote `api`

from fastapi import APIRouter

from app.api.router import api_router

# 🔁 Este router pode ser incluído no app principal (main.py)
router = APIRouter()
router.include_router(api_router)
