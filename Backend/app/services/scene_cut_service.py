# app/services/scene_cut_service.py

import os
import subprocess
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.video.io.VideoFileClip import VideoFileClip
from uuid import uuid4

def detect_scenes_and_cut(video_path: str, output_dir: str, threshold: float = 30.0) -> list[str]:
    """Detecta cenas com SceneDetect e salva os cortes com MoviePy."""
    output_files = []

    try:
        # 1. Detectar cenas com SceneDetect
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=threshold))

        video_manager.set_downscale_factor()
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list()
        video_manager.release()

        if not scene_list:
            raise Exception("Nenhuma cena detectada.")

        # 2. Cortar o vídeo com MoviePy
        for i, (start_time, end_time) in enumerate(scene_list):
            output_path = os.path.join(output_dir, f"scene_{i+1}.mp4")
            with VideoFileClip(video_path) as clip:
                new_clip = clip.subclip(start_time.get_seconds(), end_time.get_seconds())
                new_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
            output_files.append(output_path)

        return output_files

    except Exception as e:
        raise RuntimeError(f"Erro ao detectar e cortar cenas: {e}")
