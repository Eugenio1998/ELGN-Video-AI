import time
import re
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from prometheus_client import Histogram

logger = logging.getLogger(__name__)

REQUEST_TIME = Histogram(
    "http_request_duration_seconds",
    "⏱️ Tempo de resposta por método, rota e status",
    ["method", "endpoint", "status_code"]
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        raw_path = request.url.path
        path = normalize_path(raw_path)
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(f"[Prometheus] Erro ao processar requisição para {path}")
            return JSONResponse(status_code=500, content={"detail": "Erro interno no servidor."})

        duration = time.time() - start_time
        status_code = str(response.status_code)

        try:
            REQUEST_TIME.labels(method=method, endpoint=path, status_code=status_code).observe(duration)
        except Exception as e:
            logger.warning(f"[Prometheus] Erro ao registrar métrica: {e}")

        return response

def normalize_path(path: str) -> str:
    return re.sub(r"/\d+", "/:id", path)
