# 📁 backend/app/api/payments/__init__.py

from .stripe_session import router as stripe_session_router
from .webhook import router as webhook_router

# Exporta os routers da pasta payments
__all__ = ["stripe_session_router", "webhook_router"]
