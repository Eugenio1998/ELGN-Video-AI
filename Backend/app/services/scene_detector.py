import os
import cv2
import subprocess
import logging
from uuid import uuid4
from typing import List, Tuple
from fastapi import HTTPException
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from ultralytics import YOLO

# === 🛠️ Logger ===
logger = logging.getLogger("scene_detector")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 📁 TMP_DIR ===
TMP_DIR = os.getenv("TMP_DIR", "/tmp")
os.makedirs(TMP_DIR, exist_ok=True)

# === 🔍 PySceneDetect: Detecção de Cenas ===
def detect_scenes_pyscenedetect(video_path: str, threshold: float = 30.0) -> List[Tuple[float, float]]:
    logger.info(f"🎞️ Analisando cenas: {video_path} (threshold={threshold})")

    try:
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=threshold))

        video_manager.set_downscale_factor()
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)

        scenes = scene_manager.get_scene_list()
        logger.info(f"✅ {len(scenes)} cenas detectadas.")
        return [(start.get_seconds(), end.get_seconds()) for start, end in scenes]

    except Exception as e:
        logger.error(f"❌ Erro PySceneDetect: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao detectar cenas: {str(e)}")

    finally:
        if 'video_manager' in locals():
            video_manager.release()

# === 🧠 YOLO: Detecção de Objetos ===
def detect_yolo_objects(video_path: str, model_name: str = "yolov8n.pt", interval_sec: int = 2) -> List[float]:
    logger.info(f"🔍 Detectando objetos com YOLO: {video_path} (modelo={model_name})")

    try:
        model = YOLO(model_name)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Não foi possível abrir o vídeo.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = int(fps * interval_sec)
        detected_times = set()

        for frame_num in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if not ret:
                continue

            results = model(frame, verbose=False)
            if len(results[0].boxes) > 0:
                detected_times.add(frame_num / fps)

        logger.info(f"🎯 Objetos detectados em {len(detected_times)} momentos.")
        return sorted(detected_times)

    except Exception as e:
        logger.error(f"❌ Erro na detecção com YOLO: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no YOLO: {str(e)}")

    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()

# === ✂️ FFMPEG: Divisão por Cenas ===
def split_scenes(video_path: str, scene_times: List[Tuple[float, float]]) -> List[str]:
    logger.info(f"✂️ Iniciando corte do vídeo em {len(scene_times)} cenas...")

    output_files = []

    for idx, (start, end) in enumerate(scene_times):
        duration = end - start
        output_filename = f"scene_{idx+1}_{uuid4().hex[:8]}.mp4"
        output_path = os.path.join(TMP_DIR, output_filename)

        command = [
            "ffmpeg", "-y", "-i", video_path,
            "-ss", str(start), "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-ac", "2", "-b:a", "128k",
            output_path
        ]

        try:
            subprocess.run(command, check=True, capture_output=True)
            output_files.append(output_path)
            logger.info(f"✅ Cena {idx+1} salva: {output_filename}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Falha ao extrair cena {idx+1}: {e.stderr.decode()}")
            raise HTTPException(status_code=500, detail=f"Erro ao extrair cena {idx+1}")

    return output_files
