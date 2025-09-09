# 🎬 Serviços de Edição e Detecção de Cenas

import os
import shutil
import logging
from uuid import uuid4
from typing import List, Tuple

import cv2
from fastapi import UploadFile, HTTPException, Depends
from openai import ChatCompletion

from app.config import settings
from app.auth.dependencies import get_current_user
from app.models.user import User

# === 📁 Diretórios Temporários ===
STATIC_DIR = os.getenv("STATIC_DIR", "static")
VIDEOS_DIR = os.path.join(STATIC_DIR, "videos")
SCRIPTS_DIR = os.path.join(STATIC_DIR, "scripts")

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# === 🛠 Logger ===
logger = logging.getLogger("editor_service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

# === 🔐 Validação de Plano ===
def can_user_download(user: User) -> bool:
    return user and user.plan and user.plan.name.lower() not in ("basic", "gratuito")

# === 💾 Salvamento Temporário de Vídeo ===
def save_temp_video(file: UploadFile) -> str:
    """Salva o vídeo enviado em disco temporário."""
    try:
        if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
            raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

        filename = f"processed_{uuid4()}_{file.filename}"
        output_path = os.path.join(VIDEOS_DIR, filename)

        with open(output_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"📁 Vídeo salvo temporariamente em: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"❌ Falha ao salvar vídeo '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar vídeo: {str(e)}")

# === 🤖 Geração de Script com IA ===
def generate_ai_script(prompt: str, user: User = Depends(get_current_user)) -> dict:
    """Gera um script textual com IA a partir do prompt fornecido."""
    try:
        if not prompt or len(prompt.strip()) < 5:
            raise HTTPException(status_code=400, detail="Prompt inválido ou muito curto.")

        logger.info(f"🤖 Gerando script com IA a partir de: '{prompt[:50]}...'")

        response = ChatCompletion.create(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            messages=[
                {"role": "system", "content": "Você é um especialista em SEO e criação de conteúdo para vídeos."},
                {"role": "user", "content": prompt}
            ]
        )

        script = response.choices[0].message["content"].strip()
        logger.info(f"✅ Script gerado com sucesso: '{script[:100]}...'")

        return {
            "script": script,
            "can_download": can_user_download(user)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar script com IA: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar script.")

# === 🎬 Corte por Diferença de Quadros ===
def detect_scenes(video_path: str, threshold: float = 30.0) -> List[Tuple[float, float]]:
    """Detecta mudanças de cena com base na diferença de quadros."""
    scenes = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Erro ao abrir o vídeo.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    prev_frame = None
    scene_start = 0.0

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, gray)
            score = diff.mean()
            if score > threshold:
                scene_end = i / fps
                if scene_end > scene_start:
                    scenes.append((scene_start, scene_end))
                scene_start = scene_end
        prev_frame = gray

    if scene_start < duration:
        scenes.append((scene_start, duration))

    cap.release()
    return scenes

# === ✂️ Corte Automático por Histograma ===
def detect_scenes_by_histogram(
    video_path: str,
    threshold: float = 0.6,
    min_scene_length: float = 2.0,
    user: User = Depends(get_current_user)
) -> dict:
    """Detecta mudanças de cena com base em histograma de quadros."""
    logger.info(f"📽️ Iniciando detecção de cenas via histograma: {video_path}")
    scenes = []
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Não foi possível abrir o vídeo.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        prev_hist = None
        last_cut = 0.0

        for frame_num in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            if prev_hist is not None:
                diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                if diff < threshold:
                    scene_end = frame_num / fps
                    if scene_end - last_cut >= min_scene_length:
                        scenes.append({"start": last_cut, "end": scene_end})
                        last_cut = scene_end
            prev_hist = hist

        if duration - last_cut >= min_scene_length:
            scenes.append({"start": last_cut, "end": duration})

        cap.release()
        logger.info(f"✅ {len(scenes)} cenas detectadas com histograma.")
        return {
            "scenes": scenes,
            "can_download": can_user_download(user)
        }

    except Exception as e:
        logger.error(f"❌ Erro na detecção de cenas por histograma: {e}")
        return {
            "scenes": [],
            "can_download": can_user_download(user)
        }
