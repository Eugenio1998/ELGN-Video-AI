# 📁 backend/app/middleware/rate_limit.py

import os
import time
import logging
import redis
from fastapi import HTTPException
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

# === 📌 Logger configurado ===
logger = logging.getLogger(__name__)

# === 🔧 Configurações Redis ===
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("RATE_LIMIT_REDIS_DB", 1))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

# === ⚙️ Limites Globais (fallback) ===
RATE_LIMIT_DEFAULT = int(os.getenv("RATE_LIMIT", 100))           # Requisições
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 3600))    # Segundos

# === 📊 Limites por rota (customizável) ===
ROUTE_LIMITS = {
    "/auth/login": 10,
    "/auth/register": 10,
    "/auth/verify-2fa": 20,
    "/video": 60,
    "/voice": 60,
    "/image": 60,
    "/runway": 30,
    # ➕ Adicione mais rotas específicas conforme necessário
}

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        path = request.url.path

        matched_path = self.get_matched_path(path)
        limit = ROUTE_LIMITS.get(matched_path, RATE_LIMIT_DEFAULT)

        window_id = int(time.time()) // RATE_LIMIT_WINDOW
        user_id = getattr(request.state, "user_id", ip)
        key = f"ratelimit:{user_id}:{matched_path}:{window_id}"

        try:
            current = redis_client.get(key)

            if current and int(current) >= limit:
                logger.warning(f"🚫 [RateLimit] {user_id} excedeu limite de {limit} reqs em {matched_path}")
                raise HTTPException(
                    status_code=429,
                    detail=f"⏱️ Limite de {limit} requisições por {RATE_LIMIT_WINDOW // 60} minutos excedido."
                )

            pipeline = redis_client.pipeline()
            pipeline.incr(key, 1)
            if not current:
                pipeline.expire(key, RATE_LIMIT_WINDOW)
            pipeline.execute()

        except redis.exceptions.RedisError as e:
            logger.error(f"❗ [RateLimit] Erro ao acessar Redis: {e}")
            # Permite a requisição se Redis estiver indisponível

        response = await call_next(request)

        try:
            remaining = max(0, limit - int(current or 0) - 1)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
        except Exception as e:
            logger.debug(f"[RateLimit] Erro ao definir cabeçalhos: {e}")

        return response

    @staticmethod
    def get_matched_path(path: str) -> str:
        """
        Retorna o prefixo de rota mais próximo com limite configurado.
        Útil para agrupar rotas dinâmicas.
        """
        for prefix in ROUTE_LIMITS:
            if path.startswith(prefix):
                return prefix
        return "/default"
