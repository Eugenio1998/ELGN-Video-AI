import logging
from fastapi import FastAPI

from .cors import setup_cors
from .gzip import setup_gzip
from .logging_middleware import LoggingMiddleware
from .prometheus import PrometheusMiddleware
from .auth_middleware import AuthMiddleware
from .rate_limit import RateLimitMiddleware

logger = logging.getLogger(__name__)

def setup_middlewares(app: FastAPI):
    """
    Aplica todos os middlewares da aplicação.
    Ordem estratégica:
    1. CORS
    2. GZip
    3. Logging
    4. Prometheus
    5. Rate Limiting
    6. Auth
    """
    setup_cors(app)
    setup_gzip(app)

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(PrometheusMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)

    logger.info("🧩 Middlewares aplicados com sucesso.")
