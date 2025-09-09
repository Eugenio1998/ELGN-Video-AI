# 📁 backend/app/services/video_analyzer.py

import os
import cv2
import numpy as np
from pydub import AudioSegment
from scenedetect import detect, ContentDetector
import librosa
import logging

logger = logging.getLogger(__name__)
HAAR_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

# === 🎥 Análise de Movimento ===
def analyze_motion(video_path: str) -> list:
    if not os.path.exists(video_path):
        logger.error(f"❌ Arquivo de vídeo não encontrado: {video_path}")
        return []

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"❌ Não foi possível abrir o vídeo: {video_path}")
            return []

        motion_intensities = []
        prev_frame = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            if prev_frame is not None:
                diff = cv2.absdiff(prev_frame, gray)
                thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                motion_score = np.sum(thresh > 0)
                motion_intensities.append(motion_score)
            prev_frame = gray

        cap.release()
        logger.info(f"📹 Movimento analisado: {len(motion_intensities)} frames.")
        return motion_intensities
    except Exception as e:
        logger.error(f"❌ Erro na análise de movimento: {e}")
        return []

# === 😶 Análise de Rostos ===
def analyze_faces(video_path: str, sample_rate=5) -> list:
    if not os.path.exists(video_path):
        logger.error(f"❌ Arquivo de vídeo não encontrado: {video_path}")
        return []

    try:
        face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
        if face_cascade.empty():
            logger.warning("⚠️ Haar Cascade não encontrado.")
            return []

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"❌ Não foi possível abrir o vídeo: {video_path}")
            return []

        face_timestamps = []
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % sample_rate == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                if len(faces) > 0:
                    face_timestamps.append(frame_count / fps)
            frame_count += 1

        cap.release()
        logger.info(f"🧑‍🦲 Rostos detectados em {len(face_timestamps)} instantes.")
        return sorted(set(face_timestamps))
    except Exception as e:
        logger.error(f"❌ Erro na análise de rostos: {e}")
        return []

# === 🧠 Análise com YOLO ===
def analyze_objects(video_path: str, yolo_model, classes, confidence_threshold=0.5, sample_rate=5) -> dict:
    if not os.path.exists(video_path):
        logger.error(f"❌ Arquivo de vídeo não encontrado: {video_path}")
        return {}

    try:
        if yolo_model is None or classes is None:
            logger.warning("⚠️ Modelo YOLO não inicializado.")
            return {}

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"❌ Não foi possível abrir o vídeo: {video_path}")
            return {}

        detections = {}
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_count % sample_rate == 0:
                try:
                    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
                    yolo_model.setInput(blob)
                    outputs = yolo_model.forward(yolo_model.getUnconnectedOutLayersNames())
                    frame_detections = []

                    for output in outputs:
                        for detection in output:
                            scores = detection[5:]
                            class_id = np.argmax(scores)
                            confidence = scores[class_id]
                            if confidence > confidence_threshold:
                                label = classes[class_id]
                                frame_detections.append({'label': label, 'confidence': float(confidence)})

                    if frame_detections:
                        detections[frame_count / fps] = frame_detections
                except Exception as e:
                    logger.error(f"❌ Erro YOLO no frame {frame_count}: {e}")
            frame_count += 1

        cap.release()
        logger.info(f"🎯 Objetos detectados em {len(detections)} frames.")
        return detections
    except Exception as e:
        logger.error(f"❌ Erro geral em análise de objetos: {e}")
        return {}

# === 🔊 Picos de Áudio ===
def analyze_audio_peaks(video_path: str, peak_threshold=-20) -> list:
    if not os.path.exists(video_path):
        logger.error(f"❌ Arquivo de vídeo não encontrado: {video_path}")
        return []

    try:
        audio = AudioSegment.from_file(video_path)
        peaks = []
        window_ms = 50
        overlap_ms = 25

        for i in range(0, len(audio) - window_ms, overlap_ms):
            segment = audio[i:i + window_ms]
            if segment.max_dBFS > peak_threshold:
                timestamp = (i + window_ms / 2) / 1000.0
                peaks.append(timestamp)

        logger.info(f"🔊 {len(peaks)} picos de áudio detectados.")
        return sorted(set(peaks))
    except Exception as e:
        logger.error(f"❌ Erro na análise de picos de áudio: {e}")
        return []

# === 🎼 Características do Áudio ===
def analyze_audio_features(video_path: str, frame_rate=30) -> dict:
    if not os.path.exists(video_path):
        logger.error(f"❌ Arquivo de vídeo não encontrado: {video_path}")
        return {}

    try:
        y, sr = librosa.load(video_path)
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beats, sr=sr)
        features = {}

        times = librosa.frames_to_time(np.arange(centroid.shape[1]), sr=sr)
        for i, t in enumerate(times):
            data = {
                "spectral_centroid": float(centroid[0, i]),
                "is_music": any(abs(t - bt) < 0.2 for bt in beat_times)
            }
            features[float(t)] = data

        logger.info(f"🎶 Features extraídas de {len(features)} instantes.")
        return features
    except Exception as e:
        logger.error(f"❌ Erro nas features de áudio: {e}")
        return {}

# === 🎬 Agregador Geral ===
def analyze_video_for_cuts(video_path: str, yolo_model, yolo_classes, config: object) -> dict:
    return {
        "faces": analyze_faces(video_path, config.frame_sample_rate_face_object),
        "objects": analyze_objects(video_path, yolo_model, yolo_classes, sample_rate=config.frame_sample_rate_face_object),
        "audio_peaks": analyze_audio_peaks(video_path, config.audio_peak_threshold),
        "motion": analyze_motion(video_path),
        "audio_features": analyze_audio_features(video_path) if config.analyze_audio_advanced else {}
    }
