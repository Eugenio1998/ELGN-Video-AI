import os
import shutil
import logging
from uuid import uuid4
from fastapi import HTTPException

from app.services.ai_processing import process_video
from app.services.video_filters import (
    apply_opencv_filter,
    apply_moviepy_effect,
    apply_style_transfer,
    apply_banuba_filter,
)
from app.services.transcription import transcribe_video
from app.services.voice_generator import generate_voice
from app.services.scene_detector import detect_scenes_pyscenedetect, split_scenes

# === 🛠️ Logger padronizado ===
logger = logging.getLogger("processing_pipeline")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# === 🎞️ Pipeline principal ===
def full_video_pipeline(
    input_path: str,
    user_id: str,
    apply_cutting: bool = True,
    filter_type: str = None,
    filter_source: str = "opencv",
    style_model_path: str = None,
    transcribe: bool = False,
    transcription_format: str = "json",
    generate_voice_ia: bool = False,
    voice_text: str = None,
    voice_lang: str = "pt",
    voice_provider: str = "gtts",
    separar_cenas: bool = False
) -> dict:
    """
    Executa a pipeline completa de edição de vídeo com IA.
    """
    pipeline_id = str(uuid4())
    temp_dir = os.path.join("/tmp", pipeline_id)
    os.makedirs(temp_dir, exist_ok=True)
    logger.info(f"📽️ Pipeline {pipeline_id} iniciado | user_id={user_id} | arquivo={input_path}")

    try:
        base_name = pipeline_id
        current_path = input_path

        # === 1. Corte inteligente
        if apply_cutting:
            processed_path = os.path.join(temp_dir, f"cut_{base_name}.mp4")
            logger.info(f"🎬 Cortando vídeo → {processed_path}")
            process_video(current_path, processed_path)
            current_path = processed_path

        # === 2. Aplicação de filtro visual
        if filter_type:
            filtered_path = os.path.join(temp_dir, f"filtered_{base_name}.mp4")
            logger.info(f"🎨 Filtro '{filter_type}' via {filter_source} → {filtered_path}")

            if filter_source == "user_style":
                raise HTTPException(status_code=501, detail="Estilo personalizado ainda não implementado.")
            elif filter_source == "opencv":
                apply_opencv_filter(current_path, filtered_path, filter_type)
            elif filter_source == "moviepy":
                apply_moviepy_effect(current_path, filtered_path, filter_type)
            elif filter_source == "pytorch":
                if not style_model_path:
                    raise HTTPException(status_code=400, detail="Modelo de estilo ausente.")
                apply_style_transfer(current_path, filtered_path, style_model_path)
            elif filter_source == "banuba":
                apply_banuba_filter(current_path, filtered_path, filter_type)
            else:
                raise HTTPException(status_code=400, detail="Filtro inválido.")

            current_path = filtered_path

        # === 3. Transcrição
        transcription_data = None
        if transcribe:
            logger.info(f"📝 Transcrevendo vídeo (formato: {transcription_format})")
            transcription_data = transcribe_video(current_path, format=transcription_format)

        # === 4. Geração de voz IA
        voice_url = None
        if generate_voice_ia and voice_text:
            logger.info(f"🔊 Gerando voz IA | lang={voice_lang}, provider={voice_provider}")
            voice_url = generate_voice(voice_text, lang=voice_lang, provider=voice_provider)

        # === 5. Upload do vídeo final
        s3_key = f"user_{user_id}/processed/final_{base_name}.mp4"
        logger.info(f"📤 Upload vídeo final para S3 → {s3_key}")
        final_video_url = upload_to_s3(current_path, s3_key)

        # === 6. Detecção e separação de cenas
        scene_segments = []
        scene_clips_urls = []

        if separar_cenas:
            logger.info("🎞️ Separando cenas com threshold=30.0")
            scene_segments = detect_scenes_pyscenedetect(current_path, threshold=30.0)
            local_clips = split_scenes(current_path, scene_segments)

            for idx, clip_path in enumerate(local_clips):
                scene_key = f"user_{user_id}/scenes/{base_name}_scene_{idx+1}.mp4"
                logger.info(f"📤 Upload cena {idx+1} → {scene_key}")
                url = upload_to_s3(clip_path, scene_key)
                scene_clips_urls.append(url)

        # === 7. Resultado final
        result = {
            "pipeline_id": pipeline_id,
            "video_url": final_video_url,
            "transcription": transcription_data,
            "voice_url": voice_url,
            "scene_segments": scene_segments,
            "scene_clips": scene_clips_urls,
        }

        logger.info(f"✅ Pipeline {pipeline_id} finalizada com sucesso.")
        return result

    except HTTPException as http_exc:
        logger.error(f"❌ Erro HTTP | pipeline={pipeline_id} | detalhe={http_exc.detail}")
        raise http_exc

    except Exception as e:
        logger.error(f"❌ Erro inesperado | pipeline={pipeline_id} | erro={str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"🧹 Temp removido: {temp_dir}")
