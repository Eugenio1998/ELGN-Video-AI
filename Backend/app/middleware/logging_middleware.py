# 📁 backend/app/middleware/logging_middleware.py

import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("uvicorn.access")

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        request_id = request.headers.get("X-Request-ID", "-")

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            logger.exception(
                f"❌ ERRO em {method} {path} | IP: {client_ip} | RID: {request_id} | Erro: {e}"
            )
            raise

        duration = round(time.time() - start_time, 4)
        level = (
            logging.ERROR if status_code >= 500 else
            logging.WARNING if status_code >= 400 else
            logging.INFO
        )

        logger.log(
            level,
            f"{method} {path} [{status_code}] - {duration}s | IP: {client_ip} | RID: {request_id}"
        )

        return response
