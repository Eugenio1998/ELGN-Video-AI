import os
import logging
import requests
from uuid import uuid4
from fastapi import HTTPException
from datetime import datetime
from dotenv import load_dotenv

# === 🔐 Carregar .env ===
load_dotenv()
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
TMP_DIR = os.getenv("TMP_DIR", "/tmp")

# === 🛠️ Logger ===
logger = logging.getLogger("runway_gen2")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 🎬 Geração de vídeo Runway Gen-2 ===
def generate_video_from_text(
    prompt: str,
    width: int = 512,
    height: int = 512,
    seed: int = 42,
    steps: int = 25
) -> str:
    """
    Envia um prompt para o Runway Gen-2 e retorna o caminho local do vídeo gerado.
    """
    if not RUNWAY_API_KEY:
        logger.error("❌ RUNWAY_API_KEY não configurada.")
        raise HTTPException(status_code=500, detail="Chave da API Runway não configurada.")

    logger.info(f"📡 Enviando prompt para Runway Gen-2: '{prompt[:60]}...'")

    try:
        response = requests.post(
            url="https://api.runwayml.com/v1/generate",
            headers={
                "Authorization": f"Bearer {RUNWAY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt,
                "width": width,
                "height": height,
                "seed": seed,
                "num_inference_steps": steps
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()

        video_url = data.get("video")
        if not video_url:
            logger.error("⚠️ API do Runway não retornou uma URL de vídeo.")
            raise HTTPException(status_code=500, detail="API não retornou vídeo.")

        logger.info(f"🔗 Vídeo gerado pela Runway: {video_url}")

        # === 📥 Baixar vídeo ===
        filename = f"runway_gen2_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex}.mp4"
        local_path = os.path.join(TMP_DIR, filename)

        download = requests.get(video_url, timeout=120)
        download.raise_for_status()

        with open(local_path, "wb") as f:
            f.write(download.content)

        logger.info(f"✅ Vídeo salvo localmente: {local_path}")
        return local_path

    except requests.HTTPError as e:
        logger.error(f"❌ Erro HTTP ao chamar Runway: {e}")
        raise HTTPException(status_code=502, detail="Erro HTTP na API do Runway.")
    except requests.Timeout:
        logger.error("⏱️ Timeout na requisição para o Runway.")
        raise HTTPException(status_code=504, detail="Timeout na geração de vídeo com Runway.")
    except Exception as e:
        logger.error(f"🔥 Erro inesperado ao gerar vídeo: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar vídeo com Runway.")
