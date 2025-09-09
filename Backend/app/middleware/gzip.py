# 📁 backend/app/middleware/gzip.py

import logging
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

logger = logging.getLogger(__name__)

def setup_gzip(app: FastAPI):
    """
    Ativa o middleware de compressão GZip no FastAPI.

    A compressão será aplicada em respostas maiores que 500 bytes,
    reduzindo o tráfego e acelerando o carregamento para o usuário final.
    """
    app.add_middleware(GZipMiddleware, minimum_size=500)
    logger.info("🗜️ GZip ativado para respostas maiores que 500 bytes")
