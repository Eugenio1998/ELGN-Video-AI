import logging
from fastapi import APIRouter

# === 🔐 Autenticação
from app.auth.router import router as auth_router
from app.auth.register import router as register_router
from app.auth.login import router as login_router

# === 👤 Usuário
from .user import router as user_router

# === 🎥 Vídeo e Editor
from .video import router as video_router
from .editor import router as editor_router

# === 🔊 Voz
from .voice import router as voice_router
from .endpoints import voice as voice_endpoint

# === 💸 Planos e cobrança
from .billing import router as billing_router

# === 📨 Feedback
from .feedback import router as feedback_router

# === 🛠️ Admin
from .admin import router as admin_router
from app.routes import push_admin

# === 🤖 Endpoints especializados
from .endpoints import (
    videos,
    transcriptions,
    filters,
    smart_process,
    tasks,
    others
)

logger = logging.getLogger(__name__)
api_router = APIRouter()

# === ✅ INCLUSÃO DE ROTAS ===

# 🔐 Autenticação
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(register_router, prefix="/auth", tags=["Auth"])
api_router.include_router(login_router, prefix="/auth", tags=["Auth"])

# 👤 Usuário
api_router.include_router(user_router, prefix="/user", tags=["User"])

# 🎥 Vídeos e Editor
api_router.include_router(video_router, prefix="/video", tags=["Video"])
api_router.include_router(editor_router, prefix="/editor", tags=["Editor"])

# 🔊 Voz
api_router.include_router(voice_router, prefix="/voice", tags=["Voice"])
api_router.include_router(voice_endpoint.router, prefix="/voice", tags=["Voice"])

# 💳 Planos
api_router.include_router(billing_router, prefix="/billing", tags=["Billing"])

# 💬 Feedback
api_router.include_router(feedback_router, prefix="/feedback", tags=["Feedback"])

# 🛠️ Admin
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(push_admin.router, tags=["Admin"])

# 🤖 Endpoints IA especializados
api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(transcriptions.router, prefix="/transcriptions", tags=["Transcriptions"])
api_router.include_router(filters.router, prefix="/filters", tags=["Filters"])
api_router.include_router(smart_process.router, prefix="/smart-process", tags=["SmartProcess"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(others.router, prefix="/others", tags=["Others"])
