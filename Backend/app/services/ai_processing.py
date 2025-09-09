import os, cv2, subprocess, numpy as np, logging
from uuid import uuid4
from typing import List
from fastapi import UploadFile, HTTPException
from ultralytics import YOLO

# === 📁 Diretório temporário ===
TMP_DIR = "/tmp"
os.makedirs(TMP_DIR, exist_ok=True)

# === 🛠 Logger ===
logger = logging.getLogger("ai_processing")
logger.setLevel(logging.INFO)

# === 🧠 YOLOv8 ===
try:
    yolo_model = YOLO("yolov8n.pt")
    logger.info("✅ Modelo YOLO carregado com sucesso.")
except Exception as e:
    logger.error(f"❌ Falha ao carregar modelo YOLO: {e}")
    yolo_model = None

# === 🎯 Detecta momentos-chave ===
def analyze_video(video_path: str) -> List[float]:
    moments = []
    try:
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logger.info(f"📊 Analisando vídeo '{video_path}' | FPS: {fps}, Frames: {total_frames}")

        if not yolo_model:
            logger.warning("⚠️ YOLO não carregado. Pulando análise.")
            return []

        for frame_num in range(0, total_frames, fps * 2):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if not ret:
                break
            results = yolo_model(frame)
            if results[0].boxes:
                moments.append(frame_num / fps)
        cap.release()
        return sorted(set(moments))

    except Exception as e:
        logger.error(f"❌ Erro ao analisar vídeo: {e}")
        return []

# === ✂️ Processa cortes e concatena ===
def process_video(video_path: str, output_path: str):
    try:
        key_moments = analyze_video(video_path) or [10, 30, 50]
        logger.info(f"🎯 Momentos selecionados: {key_moments}")

        clips = []
        for moment in key_moments:
            start = max(0, moment - 3)
            clip_path = os.path.join(TMP_DIR, f"clip_{uuid4()}.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-i", video_path,
                "-ss", str(start), "-t", "00:00:05",
                "-c:v", "libx264", "-c:a", "aac", clip_path
            ], check=True)
            clips.append(clip_path)

        list_path = os.path.join(TMP_DIR, "concat_list.txt")
        with open(list_path, "w") as f:
            f.writelines([f"file '{c}'\n" for c in clips])

        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
            "-c:v", "libx264", "-c:a", "aac", output_path
        ], check=True)

        logger.info(f"✅ Vídeo final salvo em: {output_path}")

        # Limpeza
        for clip in clips:
            os.remove(clip)
        os.remove(list_path)

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro FFMPEG: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Erro FFMPEG: {e.stderr}")
    except Exception as e:
        logger.error(f"❌ Erro ao processar vídeo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 📤 Lida com Upload e processamento local ===
def handle_upload(file: UploadFile) -> dict:
    try:
        ext = file.filename.split(".")[-1]
        uid = f"{uuid4()}.{ext}"
        input_path = os.path.join(TMP_DIR, uid)
        output_path = os.path.join(TMP_DIR, f"processed_{uid}")

        with open(input_path, "wb") as buffer:
            buffer.write(file.file.read())

        process_video(input_path, output_path)

        result = {
            "message": "🎬 Vídeo processado com sucesso!",
            "filename": os.path.basename(output_path),
            "path": output_path
        }

        os.remove(input_path)
        os.remove(output_path)

        return result

    except Exception as e:
        logger.error(f"❌ Erro ao processar upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro geral: {e}")
