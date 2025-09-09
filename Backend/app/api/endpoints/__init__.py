# 📁 backend/app/api/endpoints/__init__.py

from fastapi import APIRouter

from .auth import router as auth_router
from .analytics import router as analytics_router
from .filters import router as filters_router
from .highlights import router as highlights_router
from .others import router as others_router
from .runway import router as runway_router
from .scene_cut import router as scene_cut_router
from .smart_process import router as smart_process_router
from .tasks import router as task_router
from .thumbnails import router as thumbnails_router
from .transcriptions import router as transcriptions_router
from .videos import router as videos_router
from .voice import router as voice_router

# === 🔀 Roteador central ===
api_router = APIRouter()

# === 📌 Registro de todos os sub-routers ===
api_router.include_router(auth_router)
api_router.include_router(analytics_router)
api_router.include_router(filters_router)
api_router.include_router(highlights_router)
api_router.include_router(others_router)
api_router.include_router(runway_router)
api_router.include_router(scene_cut_router)
api_router.include_router(smart_process_router)
api_router.include_router(task_router)
api_router.include_router(thumbnails_router)
api_router.include_router(transcriptions_router)
api_router.include_router(videos_router)
api_router.include_router(voice_router)
