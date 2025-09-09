# 📁 backend/app/services/video_processing.py

import os
import cv2
import logging
import librosa
import numpy as np
from uuid import uuid4
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from sklearn.preprocessing import MinMaxScaler
from scenedetect import detect, ContentDetector

# === 🔧 Configurações ===
load_dotenv()
TMP_DIR = os.getenv("TMP_DIR", "/tmp")

# === 🛠️ Logger Setup ===
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === 🎥 Análise de Movimento ===
def analyze_motion(video_path: str) -> List[float]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Não foi possível abrir o vídeo: {video_path}")
        return []

    prev_frame = None
    intensities = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, gray)
            thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            motion_score = np.sum(thresh) / float(thresh.size)
            intensities.append(motion_score)
        prev_frame = gray

    cap.release()
    return intensities

# === 🔊 Picos de Áudio ===
def analyze_audio_peaks(video_path: str, threshold: int = -20) -> List[float]:
    try:
        audio = AudioSegment.from_file(video_path)
    except Exception as e:
        logger.error(f"Erro ao carregar áudio: {e}")
        return []

    peaks = []
    window_ms, overlap = 50, 25

    for i in range(0, len(audio) - window_ms, overlap):
        seg = audio[i:i+window_ms]
        if seg.max_dBFS > threshold:
            peak_time = (i + window_ms / 2) / 1000.0
            peaks.append(peak_time)

    return sorted(set(peaks))

# === 🎼 Características Avançadas de Áudio ===
def analyze_audio_features(video_path: str) -> dict:
    try:
        y, sr = librosa.load(video_path)
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beats, sr=sr)
        audio_features = {}
        for i, t in enumerate(librosa.frames_to_time(np.arange(len(centroid)), sr=sr)):
            audio_features[t] = {
                "spectral_centroid": centroid[i],
                "is_music": any(abs(t - bt) < 0.2 for bt in beat_times)
            }
        return audio_features
    except Exception as e:
        logger.error(f"Erro em audio_features: {e}")
        return {}

# === ✂️ Corte de Segmentos ===
def cut_video_segments(video_path: str, segments: List[Tuple[float, float]]) -> List[str]:
    clip = VideoFileClip(video_path)
    paths = []
    for idx, (start, end) in enumerate(segments):
        subclip = clip.subclip(start, end)
        out_path = os.path.join(TMP_DIR, f"cut_{idx+1}_{uuid4()}.mp4")
        subclip.write_videofile(out_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        paths.append(out_path)
    clip.close()
    return paths

# === 🧠 Análise de Cenas e Segmentos ===
def analyze_video_for_cuts(
    video_path: str,
    use_scene_detection=True,
    min_cut_duration=1.0,
    max_cut_duration=10.0,
    scene_threshold=20.0,
    motion_weight=0.3,
    audio_weight=0.4,
    face_weight=0.5,
    object_weight=0.6,
    max_num_cuts=5,
    audio_peak_threshold=-20,
    analyze_audio_advanced=False,
    speech_weight=0.3,
    music_weight=0.2,
    yolo_model=None,
    yolo_classes=None
) -> List[Tuple[float, float]]:
    
    motion = analyze_motion(video_path)
    motion_scaled = MinMaxScaler().fit_transform(np.array(motion).reshape(-1, 1)).flatten() if motion else []
    audio_peaks = analyze_audio_peaks(video_path, audio_peak_threshold)
    audio_features = analyze_audio_features(video_path) if analyze_audio_advanced else {}

    try:
        clip = VideoFileClip(video_path)
        fps = clip.fps
        duration = clip.duration
    except Exception as e:
        logger.error(f"Erro ao abrir video: {e}")
        return []

    segments = []

    if use_scene_detection:
        scenes = detect(video_path, ContentDetector(threshold=scene_threshold))
        for scene in scenes:
            start, end = scene[0].get_seconds(), scene[1].get_seconds()
            duration_seg = end - start
            if min_cut_duration <= duration_seg <= max_cut_duration:
                score = 1.0
                mid_time = (start + end) / 2
                score += audio_weight if any(abs(mid_time - t) < 0.5 for t in audio_peaks) else 0
                score += motion_weight * (motion_scaled[int(mid_time * fps)] if motion_scaled else 0)
                score += speech_weight if any(abs(mid_time - t) < 0.5 and v.get('spectral_centroid', 0) > 3000 for t, v in audio_features.items()) else 0
                score += music_weight * 0.5 if any(abs(mid_time - t) < 0.5 and v.get('is_music') for t, v in audio_features.items()) else 0
                segments.append((start, end, score))

    if not segments:
        for t in audio_peaks:
            if min_cut_duration < t < (duration - min_cut_duration):
                segments.append((max(0, t-1), min(duration, t+1), 0.6))

    segments.sort(key=lambda x: x[2], reverse=True)
    final_cuts = []
    last_end = -float("inf")
    for start, end, _ in segments:
        if len(final_cuts) >= max_num_cuts:
            break
        if start > last_end + min_cut_duration:
            final_cuts.append((start, end))
            last_end = end

    return final_cuts
