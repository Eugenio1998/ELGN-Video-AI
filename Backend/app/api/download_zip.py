import os
import uuid
import aiohttp
import zipfile
import logging
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl

# === CONFIGURAÇÕES ===
TEMP_DIR = "temp_zips"
os.makedirs(TEMP_DIR, exist_ok=True)

router = APIRouter(prefix="/zip", tags=["Downloads"])
logger = logging.getLogger(__name__)

# === MODELO DE ENTRADA ===

class DownloadZipRequest(BaseModel):
    video: HttpUrl
    audio: HttpUrl
    image: HttpUrl

# === UTILITÁRIO: Remoção de arquivo após envio ===

def remove_temp_file(path: str):
    try:
        os.remove(path)
        logger.info(f"🧹 Arquivo temporário removido: {path}")
    except Exception as e:
        logger.warning(f"Erro ao remover arquivo temporário {path}: {e}")

# === ENDPOINT: Geração de ZIP com vídeo, áudio e imagem ===

@router.post("/download-all")
async def download_zip(payload: DownloadZipRequest, background_tasks: BackgroundTasks):
    """
    Recebe URLs de vídeo, áudio e imagem. Retorna um arquivo ZIP com os três.
    """
    zip_id = str(uuid.uuid4())
    zip_path = os.path.join(TEMP_DIR, f"{zip_id}.zip")

    files = [
        ("video.mp4", payload.video),
        ("audio.mp3", payload.audio),
        ("image.png", payload.image),
    ]

    try:
        async with aiohttp.ClientSession() as session:
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for filename, url in files:
                    try:
                        async with session.get(str(url)) as response:
                            if response.status == 200:
                                content = await response.read()
                                zipf.writestr(filename, content)
                                logger.info(f"✅ Adicionado ao zip: {filename} ({url})")
                            else:
                                logger.error(f"❌ Falha ao baixar {filename} de {url} - status {response.status}")
                                return JSONResponse(
                                    status_code=400,
                                    content={"error": f"Erro ao baixar {filename} (status {response.status})."}
                                )
                    except Exception as e:
                        logger.exception(f"❌ Erro ao baixar {filename} de {url}")
                        return JSONResponse(status_code=500, content={"error": f"Erro ao baixar {filename}: {str(e)}"})

        logger.info(f"📦 ZIP gerado com sucesso: {zip_path}")
        background_tasks.add_task(remove_temp_file, zip_path)

        return FileResponse(
            path=zip_path,
            filename="criacoes_elgn.zip",
            media_type="application/zip"
        )

    except Exception as e:
        logger.exception(f"❌ Erro inesperado ao gerar o ZIP")
        return JSONResponse(status_code=500, content={"error": "Erro ao gerar o ZIP."})
