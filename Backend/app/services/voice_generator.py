# 📁 app/services/voice_generator.py

import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv, find_dotenv
from app.utils.logger import log_info

# === 🔄 Carregar variáveis de ambiente ===
load_dotenv(find_dotenv())

# === 🔐 Chave da API ElevenLabs ===
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("❌ A chave da API da ElevenLabs (ELEVENLABS_API_KEY) não está definida no .env.")

# === 🧠 Função de Geração de Voz com ElevenLabs ===
def generate_voice(
    text: str,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model_id: str = "eleven_monolingual_v1"
) -> bytes:
    """
    Gera voz a partir de texto usando ElevenLabs.

    Args:
        text (str): Texto a ser convertido em voz.
        voice_id (str): ID da voz desejada.
        model_id (str): ID do modelo de voz.

    Returns:
        bytes: Áudio gerado em bytes.
    """
    log_info("🔊 Gerando voz com ElevenLabs...")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        log_info("✅ Voz gerada com sucesso via ElevenLabs.")
        return response.content
    except requests.exceptions.RequestException as e:
        log_info("❌ Erro ao chamar API da ElevenLabs.")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar voz: {str(e)}")
