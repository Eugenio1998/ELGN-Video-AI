# 📁 backend/app/routes/scenes.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.scene_detector import detect_scenes_pyscenedetect, split_scenes
from app.services.redis_cache import cache_get, cache_set
from app.auth.dependencies import get_current_user
from app.models.user import User

from pathlib import Path
from hashlib import md5
from uuid import uuid4
from typing import List
import logging
import os

router = APIRouter(tags=["Scenes"])

# === 📁 Configurações ===
SCENE_CACHE_PREFIX = "scenes"
SCENE_CLIPS_DIR = Path("static/scenes")
SCENE_CLIPS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("scene_routes")
logger.setLevel(logging.INFO)

# === 🎬 Detectar Cenas ===
@router.post("/scenes/", dependencies=[Depends(get_current_user)])
async def detect_scenes(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    🎬 Detecta cenas em um vídeo e retorna URLs dos clipes gerados.
    Utiliza cache para acelerar chamadas repetidas.
    """
    try:
        file_bytes = await file.read()
        file_hash = md5(file_bytes).hexdigest()
        cache_key = f"{SCENE_CACHE_PREFIX}:{file_hash}"

        cached = cache_get(cache_key)
        if cached:
            logger.info(f"🔁 [CACHE] Resultado reutilizado para '{file.filename}' por {current_user.username}")
            return {"cached": True, **cached}

        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else None
        if not ext:
            raise HTTPException(status_code=400, detail="Arquivo enviado sem extensão válida.")

        unique_filename = f"{uuid4()}.{ext}"
        input_path = Path("/tmp") / unique_filename
        input_path.write_bytes(file_bytes)

        logger.info(f"📥 Vídeo recebido '{file.filename}' salvo como '{unique_filename}' por {current_user.username}")

        scenes = detect_scenes_pyscenedetect(str(input_path))
        if not scenes:
            logger.info(f"⚠️ Nenhuma cena detectada no vídeo '{file.filename}'")
            input_path.unlink(missing_ok=True)
            return {"message": "Nenhuma cena detectada."}

        clips = split_scenes(str(input_path), scenes, output_dir=str(SCENE_CLIPS_DIR))
        clip_urls: List[str] = [f"/static/scenes/{Path(c).name}" for c in clips]

        logger.info(f"✅ {len(clips)} clipes gerados com sucesso para '{file.filename}'")

        result = {"scene_segments": scenes, "scene_clips": clip_urls}
        cache_set(cache_key, result, expiration=3600)
        logger.info(f"📦 Resultado cacheado com sucesso (hash={file_hash})")

        input_path.unlink(missing_ok=True)
        return {"cached": False, **result}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Erro inesperado ao processar '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar vídeo: {str(e)}")


# === 📺 Simular Streaming ===
@router.get("/scenes/stream")
def stream_scene(index: int):
    """
    📺 Retorna o URL do clipe de cena simulando um streaming.
    """
    try:
        all_clips = sorted(SCENE_CLIPS_DIR.glob("*.mp4"))
        if index < 0 or index >= len(all_clips):
            raise HTTPException(status_code=404, detail="Cena não encontrada.")

        selected = all_clips[index]
        return {"url": f"/static/scenes/{selected.name}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao obter clipe de índice {index}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
