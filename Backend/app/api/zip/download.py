import io
import logging
from zipfile import ZipFile
from urllib.parse import urlparse
from pathlib import Path
import re

import aiohttp
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl, constr
from typing import List

from app.api.error_response import ErrorResponse
from app.dependencies.access_control import get_current_user  # 🔐 Controle de acesso

# === Logger ===
logger = logging.getLogger(__name__)

# === Router ===
router = APIRouter(prefix="/zip", tags=["Downloads"])

# === SCHEMAS ===
class ZipVideoItem(BaseModel):
    url: HttpUrl
    title: constr(min_length=1, max_length=64)

class ZipRequestPayload(BaseModel):
    videos: List[ZipVideoItem]

# === UTILS ===
def sanitize_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name.strip())

# === ENDPOINT: Baixar vários vídeos em ZIP ===
@router.post(
    "/download",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def download_zip(
    payload: ZipRequestPayload,
    user=Depends(get_current_user)  # 🔐 Somente usuários autenticados
):
    """
    Recebe uma lista de URLs de vídeos e retorna um ZIP com os arquivos baixados.
    """
    if not payload.videos:
        logger.warning("❌ Nenhum vídeo recebido para download.")
        raise HTTPException(status_code=400, detail="Nenhum vídeo recebido.")

    if len(payload.videos) > 20:
        logger.warning("⚠️ Limite excedido: mais de 20 vídeos.")
        raise HTTPException(status_code=400, detail="Máximo de 20 vídeos por requisição.")

    zip_io = io.BytesIO()

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            with ZipFile(zip_io, mode="w") as zipf:
                for item in payload.videos:
                    try:
                        async with session.get(item.url) as resp:
                            if resp.status != 200:
                                logger.warning(f"⚠️ Erro ao baixar {item.url} (status {resp.status})")
                                continue

                            content = await resp.read()
                            ext = Path(urlparse(item.url).path).suffix.lstrip(".") or "mp4"
                            filename = f"{sanitize_filename(item.title)}.{ext}"
                            zipf.writestr(filename, content)
                            logger.info(f"📦 Adicionado ao ZIP: {filename}")

                    except Exception as e:
                        logger.error(f"❌ Falha ao processar {item.url}: {e}")
                        continue

        zip_io.seek(0)
        return StreamingResponse(
            zip_io,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=meus-videos.zip"}
        )

    except Exception as e:
        logger.error(f"❌ Erro geral ao criar ZIP: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar o arquivo ZIP.")
