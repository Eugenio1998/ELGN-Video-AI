# 📂 app/tasks.py

from app.celery_app import celery_app
from app.services import transcription, video_filters, voice_generator, video_processing, usage_limits
from app.video_analyzer import analyze_motion, analyze_faces, analyze_objects, analyze_audio_peaks, VideoAnalysisConfig
from app.config import settings
from moviepy.editor import VideoFileClip, concatenate_videoclips
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy.orm import Session
from typing import Optional
from celery import shared_task, group
from celery.utils.log import get_task_logger
import requests
import numpy as np
import cv2
import os
import time

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3)
def unreliable_task(self):
    try:
        if time.time() % 5 > 4:
            raise Exception("Erro simulado!")
        return {"result": "Tarefa bem-sucedida."}
    except Exception as exc:
        logger.error(f"Tarefa falhou: {exc}. Tentativa {self.request.retries + 1} de {self.max_retries}.")
        raise self.retry(exc=exc, countdown=5)

@shared_task
def transcribe_video_task(video_path):
    logger.info(f"Iniciando transcrição de: {video_path}")
    result = transcription.transcribe_video(video_path)
    logger.info(f"Transcrição concluída.")
    return result

@shared_task
def generate_voice_task(text: str, lang: str = "pt", provider: str = "gtts", voice: str = "nova"):
    try:
        audio_url = voice_generator.generate_voice(text, lang, provider, voice)
        return {"status": "success", "audio_url": audio_url}
    except Exception as e:
        logger.error(f"Erro ao gerar voz: {e}")
        return {"status": "error", "error": str(e)}

@shared_task
def apply_video_filter_task(input_path: str, output_path: str, filter_type: str):
    try:
        video_filters.apply_opencv_filter(input_path, output_path, filter_type)
        return {"status": "success", "output_path": output_path, "filter_applied": filter_type}
    except Exception as e:
        logger.error(f"Erro ao aplicar filtro: {e}")
        return {"status": "error", "error": str(e)}

@shared_task
def process_video_transcription(video_path: str, output_path: str, audio_language: str = "pt"):
    try:
        result = transcription.transcribe_video(video_path, output_path, audio_language)
        return {"status": "success", "transcription_path": output_path, "result": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@shared_task
def process_smart_video_cut_task(video_path: str, output_dir: str, use_scene_detection: bool = True, min_cut_duration: float = 1.0, max_cut_duration: float = 10.0, threshold_intensity: float = 20.0):
    try:
        cut_files = video_processing.process_video(
            video_path,
            output_dir,
            use_scene_detection=use_scene_detection,
            min_cut_duration=min_cut_duration,
            max_cut_duration=max_cut_duration,
            threshold_intensity=threshold_intensity
        )
        return {"status": "success", "cut_files": cut_files}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@shared_task
def check_user_usage_task(user_id: str, plan: str):
    try:
        usage_data = usage_limits.check_and_update_usage(user_id, plan)
        return {"status": "success", "usage_data": usage_data}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@shared_task
def analyze_viewer_attention_task(video_id, platform_api_url, api_key):
    try:
        url = f"{platform_api_url}/videos/{video_id}/analytics/retention"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        retention_data = response.json()

        drop_off_points = []
        if 'retention_curve' in retention_data:
            curve = retention_data['retention_curve']
            for i in range(1, len(curve)):
                if curve[i-1] - curve[i] > 0.1:
                    drop_off_points.append(i / len(curve) * 60.0)

        return {"video_id": video_id, "drop_off_points": drop_off_points}
    except Exception as e:
        return {"video_id": video_id, "error": str(e)}

@shared_task
def suggest_edits_for_retention_task(attention_data, video_path):
    suggestions = []
    if 'drop_off_points' in attention_data:
        for point in attention_data['drop_off_points']:
            suggestions.append(f"Corte sugerido em torno de {point:.2f} segundos.")
    return {"video_id": attention_data.get('video_id'), "suggestions": suggestions}

@shared_task
def generate_video_highlights_task(video_path, highlight_duration=30, config_params=None):
    try:
        config = VideoAnalysisConfig(**(config_params or {}))
        motion = analyze_motion(video_path)
        faces = analyze_faces(video_path, sample_rate=config.frame_sample_rate_face_object)
        objects = analyze_objects(video_path, None, None, sample_rate=config.frame_sample_rate_face_object)
        audio_peaks = analyze_audio_peaks(video_path, peak_threshold=config.audio_peak_threshold)

        potential = []
        clip = VideoFileClip(video_path)
        duration = clip.duration
        fps = clip.fps

        if motion:
            normalized = MinMaxScaler().fit_transform(np.array(motion).reshape(-1, 1)).flatten()
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(normalized, height=0.5, distance=int(fps * 2))
            for peak in peaks:
                t = peak / fps
                start = max(0, t - 2)
                end = min(duration, t + 3)
                score = normalized[peak]
                if any(abs(t - ts) < 1 for ts in faces): score += 0.3
                if any(start <= ts <= end for ts in objects): score += 0.2
                if any(start <= ts <= end for ts in audio_peaks): score += 0.1
                potential.append({'start': start, 'end': end, 'score': score})

        highlights = sorted(potential, key=lambda x: x['score'], reverse=True)
        selected = []
        total = 0
        for s in highlights:
            if total + (s['end'] - s['start']) <= highlight_duration:
                selected.append((s['start'], s['end']))
                total += (s['end'] - s['start'])
                if total >= highlight_duration:
                    break

        clips = [clip.subclip(start, end) for start, end in selected]
        final = concatenate_videoclips(clips)
        output = f"highlight_{os.path.basename(video_path)}"
        final.write_videofile(output, codec="libx264", audio_codec="aac")
        clip.close()
        final.close()
        return {"video_id": os.path.basename(video_path), "highlight_path": output}

    except Exception as e:
        return {"video_id": os.path.basename(video_path), "error": str(e)}

@shared_task
def analyze_sentiment_task(transcription_result: dict):
    from transformers import pipeline

    try:
        # Garante que tem texto na transcrição
        text = transcription_result.get("text") or transcription_result.get("result")
        if not text:
            raise ValueError("Nenhum texto encontrado para análise de sentimento.")

        # Carrega o pipeline de sentimento em português
        sentiment_analyzer = pipeline("sentiment-analysis", model="pierreguillou/bert-base-cased-sentiment-analysis")
        
        # Aplica análise
        result = sentiment_analyzer(text[:512])  # limita para 512 tokens
        sentiment = result[0]["label"]

        return {
            "text": text,
            "sentiment": sentiment,
            "score": result[0]["score"]
        }

    except Exception as e:
        logger.error(f"Erro na análise de sentimento: {e}")
        return {"error": str(e)}

@shared_task
def cut_video_by_moments_task(sentiment_result: dict, video_path: str):
    try:
        # Lógica fictícia de corte baseado em sentimento
        timestamps = sentiment_result.get("highlights", [])
        if not timestamps:
            return {"status": "no_cuts", "message": "Nenhum momento emocional identificado."}

        return {"status": "success", "moments": timestamps}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    
    # === 🧠 Thumbnail Inteligente ===
@shared_task
def generate_intelligent_thumbnail_task(video_path: str, output_path: Optional[str] = None):
    try:
        logger.info(f"📸 Gerando thumbnail inteligente para: {video_path}")

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {video_path}")

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        mid_frame = total_frames // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
        success, frame = cap.read()

        if not success:
            raise Exception("Erro ao capturar frame do vídeo.")

        # Define caminho padrão de saída se não for fornecido
        if not output_path:
            base_name = os.path.basename(video_path).split('.')[0]
            output_path = f"/tmp/{base_name}_thumbnail.jpg"

        cv2.imwrite(output_path, frame)
        cap.release()

        logger.info(f"✅ Thumbnail salva em: {output_path}")
        return {"status": "success", "thumbnail_path": output_path}

    except Exception as e:
        logger.error(f"Erro ao gerar thumbnail: {e}")
        return {"status": "error", "error": str(e)}
