# 🎬 Serviços de Corte e Edição de Vídeo

import os
import logging
from typing import List, Tuple
from moviepy.editor import VideoFileClip, concatenate_videoclips
import cv2

# === 🛠️ Logger ===
logger = logging.getLogger("editor")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === ✂️ Corte Único ===
def apply_cut(video_path: str, start_time: float, end_time: float, output_path: str) -> str | None:
    """Aplica um único corte a um vídeo."""
    logger.info(f"✂️ Corte: {video_path} [{start_time}-{end_time}] => {output_path}")
    try:
        if not os.path.exists(video_path):
            logger.error(f"❌ Arquivo não encontrado: {video_path}")
            return None

        with VideoFileClip(video_path) as clip:
            if start_time < 0 or end_time > clip.duration or start_time >= end_time:
                logger.warning(f"⚠️ Intervalo inválido: [{start_time}-{end_time}] (duração: {clip.duration})")
                return None

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            clip.subclip(start_time, end_time).write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

        logger.info(f"✅ Corte salvo em: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"❌ Erro ao cortar vídeo: {e}")
        return None

# === ✂️ Múltiplos Cortes ===
def apply_multiple_cuts(video_path: str, cuts: List[dict], output_dir: str, base_name: str = "cut") -> List[str]:
    """Aplica vários cortes em um vídeo, gerando arquivos separados."""
    logger.info(f"📎 Múltiplos cortes em: {video_path} => {output_dir}")
    cut_files = []

    try:
        if not os.path.exists(video_path):
            logger.error(f"❌ Vídeo não encontrado: {video_path}")
            return []

        with VideoFileClip(video_path) as clip:
            os.makedirs(output_dir, exist_ok=True)

            for i, cut in enumerate(cuts):
                start = cut.get("start")
                end = cut.get("end")
                if start is not None and end is not None and 0 <= start < end <= clip.duration:
                    out_path = os.path.join(output_dir, f"{base_name}_{i+1}.mp4")
                    logger.info(f"⏱️ Corte {i+1}: [{start}-{end}] => {out_path}")
                    clip.subclip(start, end).write_videofile(out_path, codec="libx264", audio_codec="aac", logger=None)
                    cut_files.append(out_path)
                else:
                    logger.warning(f"⚠️ Corte inválido ignorado: {cut}")

        logger.info(f"✅ Total de cortes realizados: {len(cut_files)}")
        return cut_files
    except Exception as e:
        logger.error(f"❌ Erro ao aplicar múltiplos cortes: {e}")
        return []

# === 🔗 Concatenar Vídeos ===
def concatenate_video_segments(video_paths: List[str], output_path: str) -> str | None:
    """Concatena uma lista de vídeos em um único arquivo."""
    logger.info(f"🔗 Concatenando vídeos: {video_paths} => {output_path}")
    clips = []

    try:
        for path in video_paths:
            if os.path.exists(path):
                clips.append(VideoFileClip(path))
            else:
                logger.warning(f"⚠️ Ignorado (não encontrado): {path}")

        if not clips:
            logger.error("❌ Nenhum vídeo válido para concatenação.")
            return None

        final = concatenate_videoclips(clips)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

        logger.info(f"✅ Concatenação salva em: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"❌ Erro ao concatenar vídeos: {e}")
        return None
    finally:
        for clip in clips:
            clip.close()

# === 🎬 Detecção de Cenas ===
def detect_scenes(video_path: str, threshold: float = 30.0) -> List[Tuple[float, float]]:
    """
    Detecta cenas com base na diferença entre quadros consecutivos.
    Retorna uma lista de (start_time, end_time).
    """
    logger.info(f"🎬 Iniciando detecção de cenas: {video_path}")
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
    logger.info(f"✅ Cenas detectadas: {len(scenes)}")
    return scenes
