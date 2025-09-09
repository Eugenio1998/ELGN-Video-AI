# 📁 backend/app/middleware/auth_middleware.py

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError, ExpiredSignatureError

from app.config import settings

logger = logging.getLogger(__name__)

# 🔐 Rotas que requerem autenticação
PROTECTED_PATHS = ("/user", "/video", "/voice", "/billing", "/feedback", "/admin")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 🚧 Verifica se a rota acessada é protegida
        if any(path.startswith(prefix) for prefix in PROTECTED_PATHS):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                logger.warning(f"🔒 Token ausente ou malformado na rota: {path}")
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token ausente ou inválido"}
                )

            token = auth_header.split("Bearer ")[-1].strip()

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                request.state.user_id = payload.get("sub")
                logger.debug(f"🔑 Token válido para user_id: {request.state.user_id}")

            except ExpiredSignatureError:
                logger.warning("⏰ Token expirado.")
                return JSONResponse(status_code=401, content={"detail": "Token expirado"})

            except JWTError as e:
                logger.warning(f"❌ Erro no JWT: {e}")
                return JSONResponse(status_code=403, content={"detail": "Token inválido"})

        # ✅ Requisição continua normalmente
        return await call_next(request)
