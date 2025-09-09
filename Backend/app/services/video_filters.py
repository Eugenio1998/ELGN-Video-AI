# 📁 backend/app/services/video_filters.py

import os
import cv2
import torch
import logging
import numpy as np
import tempfile
from uuid import uuid4
from PIL import Image
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, vfx
from torchvision import transforms
from fastapi import HTTPException
import requests
import openai

# === 🔐 Carregar variáveis de ambiente ===
load_dotenv()
BANUBA_API_KEY = os.getenv("BANUBA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

TMP_DIR = "/tmp" if os.path.exists("/tmp") else tempfile.gettempdir()

# === 🛠️ Logging Setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

# === 🎨 Filtros com OpenCV ===
def apply_opencv_filter(input_path: str, output_path: str, filter_type: str):
    if not os.path.exists(input_path):
        logger.error(f"Arquivo de vídeo não encontrado: {input_path}")
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado.")

    logger.info(f"Aplicando filtro OpenCV '{filter_type}' em '{input_path}' → '{output_path}'")
    try:
        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        if not out.isOpened():
            raise Exception("Falha ao inicializar o gravador de vídeo.")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if filter_type == "gray":
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif filter_type == "sepia":
                sepia = np.array([[0.272, 0.534, 0.131],
                                  [0.349, 0.686, 0.168],
                                  [0.393, 0.769, 0.189]])
                frame = cv2.transform(frame, sepia)
                frame = np.clip(frame, 0, 255).astype(np.uint8)
            elif filter_type == "blur":
                frame = cv2.GaussianBlur(frame, (15, 15), 0)
            else:
                raise HTTPException(status_code=400, detail="Filtro OpenCV inválido.")

            out.write(frame)

        cap.release()
        out.release()
        logger.info(f"✅ Filtro OpenCV '{filter_type}' aplicado com sucesso.")
    except Exception as e:
        logger.error(f"❌ Erro ao aplicar filtro OpenCV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 🎬 Efeitos com MoviePy ===
def apply_moviepy_effect(input_path: str, output_path: str, effect: str):
    if not os.path.exists(input_path):
        logger.error(f"Arquivo de vídeo não encontrado: {input_path}")
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado.")

    logger.info(f"Aplicando efeito MoviePy '{effect}' em '{input_path}' → '{output_path}'")
    try:
        clip = VideoFileClip(input_path)

        if effect == "color_boost":
            result = clip.fx(vfx.colorx, 1.4)
        elif effect == "fadein":
            result = clip.fx(vfx.fadein, 1)
        elif effect == "fadeout":
            result = clip.fx(vfx.fadeout, 1)
        else:
            raise HTTPException(status_code=400, detail="Efeito MoviePy inválido.")

        result.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)
        clip.close()
        logger.info(f"✅ Efeito MoviePy '{effect}' aplicado com sucesso.")
    except Exception as e:
        logger.error(f"❌ Erro MoviePy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 🧠 Transferência de Estilo com PyTorch ===
def apply_style_transfer(input_path: str, output_path: str, model_path: str):
    if not os.path.exists(input_path) or not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Arquivo de vídeo ou modelo não encontrado.")

    logger.info(f"Aplicando style transfer com modelo '{model_path}'")
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = torch.jit.load(model_path).to(device).eval()

        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

        preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.mul(255))
        ])

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            tensor = preprocess(Image.fromarray(rgb).resize((width, height))).unsqueeze(0).to(device)

            with torch.no_grad():
                result = model(tensor).cpu().squeeze().clamp(0, 255).numpy()
                frame_out = result.transpose(1, 2, 0).astype("uint8")
                out.write(cv2.cvtColor(frame_out, cv2.COLOR_RGB2BGR))

        cap.release()
        out.release()
        logger.info("✅ Style transfer concluído com sucesso.")
    except Exception as e:
        logger.error(f"❌ Erro na IA Style Transfer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ☁️ Filtro via API Banuba ===
def apply_banuba_filter(input_path: str, output_path: str, filter_name: str):
    if not BANUBA_API_KEY:
        raise HTTPException(status_code=500, detail="Chave da API Banuba não configurada.")
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado.")

    logger.info(f"Usando API Banuba: '{filter_name}' em '{input_path}'")
    try:
        with open(input_path, "rb") as file:
            response = requests.post(
                "https://api.banuba.com/video/filter",
                headers={"X-Api-Key": BANUBA_API_KEY},
                data={"filter": filter_name},
                files={"video": file}
            )
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(response.content)
        logger.info(f"✅ Filtro Banuba '{filter_name}' aplicado com sucesso.")
    except requests.RequestException as e:
        logger.error(f"❌ Erro Banuba: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 🔊 Geração de Voz com OpenAI ===
def generate_voice_openai(text: str, voice: str = "nova", lang: str = "pt-BR") -> str:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Chave da API OpenAI não configurada.")

    output_path = f"{TMP_DIR}/voice_{uuid4()}.mp3"
    logger.info(f"🔈 OpenAI TTS → '{output_path}'")
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3"
        )
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    except Exception as e:
        logger.error(f"❌ Erro TTS OpenAI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 🗣️ Geração de Voz com ElevenLabs ===
def generate_voice_elevenlabs(text: str, voice_id: str, api_key: str = None) -> str:
    if not api_key:
        raise HTTPException(status_code=400, detail="Chave da API ElevenLabs não fornecida.")

    output_path = f"{TMP_DIR}/voice_{uuid4()}.mp3"
    logger.info(f"🔈 ElevenLabs TTS → '{output_path}'")
    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
        )
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    except requests.RequestException as e:
        logger.error(f"❌ Erro ElevenLabs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === ✂️ Corte Automático por Cenas ===
def split_video_by_scene(input_path: str, output_dir: str) -> list:
    logger.info(f"🧩 Iniciando corte por cenas: {input_path}")
    try:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise Exception("Falha ao abrir o vídeo.")

        scene_paths = []
        scene_id = 0
        last_hist = None
        threshold = 0.5
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = None
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            if last_hist is not None:
                correlation = cv2.compareHist(last_hist, hist, cv2.HISTCMP_CORREL)
                if correlation < threshold:
                    if out:
                        out.release()
                    scene_id += 1
                    logger.info(f"🔪 Nova cena detectada no frame {frame_idx} (corr: {correlation:.2f})")

            if out is None or not out.isOpened():
                scene_path = os.path.join(output_dir, f"scene_{scene_id:03}.mp4")
                out = cv2.VideoWriter(scene_path, fourcc, fps, (width, height))
                scene_paths.append(scene_path)

            out.write(frame)
            last_hist = hist
            frame_idx += 1

        cap.release()
        if out:
            out.release()
        logger.info(f"✅ Corte concluído com {len(scene_paths)} cenas.")
        return scene_paths
    except Exception as e:
        logger.error(f"❌ Erro corte por cenas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
