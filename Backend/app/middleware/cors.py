# 📁 backend/app/middleware/cors.py


import os
import logging
from urllib.parse import urlparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

def add_cors_middleware(app: FastAPI):
    """
    Adiciona middleware CORS com base na variável de ambiente CORS_ALLOWED_ORIGINS.
    Exemplo de uso no .env:
        CORS_ALLOWED_ORIGINS=http://localhost:3000,https://meusite.com
    """
    origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
    allowed_origins = []

    if origins_env:
        for origin in origins_env.split(","):
            origin = origin.strip()
            parsed = urlparse(origin)
            if parsed.scheme in ("http", "https"):
                allowed_origins.append(origin)
            else:
                logger.warning(f"🌐 Origem inválida ignorada: {origin}")
    else:
        # fallback local
        allowed_origins = ["http://localhost:3000"]
        logger.warning("⚠️ Nenhuma origem definida. Usando fallback: http://localhost:3000")

    logger.info(f"✅ CORS ativado para: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_cors(app: FastAPI):
    """
    Alternativa: Middleware de CORS aberto (recomendado apenas para testes locais).
    """
    logger.warning("🚨 Usando setup_cors com CORS aberto. Não recomendado para produção.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
