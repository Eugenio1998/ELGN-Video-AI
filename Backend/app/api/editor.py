import os
import json
import logging
from uuid import uuid4
from typing import List

from fastapi import APIRouter, UploadFile, Form, File, Request, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.config import settings
from app.database import get_db
from app.services import editor_service
from app.services.editor import apply_cut, apply_multiple_cuts, concatenate_video_segments

router = APIRouter(prefix="/editor", tags=["Editor AI"])
logger = logging.getLogger(__name__)
TMP_DIR = settings.TMP_DIR

# === 📦 SCHEMAS ===

class ScriptGenerationInput(BaseModel):
    prompt: str

class VideoProcessingInput(BaseModel):
    enhancements: str
    seo: str
    resolution: str
    aspectRatio: str

# === 🔧 UTILITÁRIO ===

async def save_upload_file(upload_file: UploadFile) -> str:
    """Salva o arquivo de upload temporariamente e retorna o caminho."""
    extension = upload_file.filename.split(".")[-1].lower()
    if extension not in ["mp4", "mov", "avi", "mkv"]:
        raise HTTPException(status_code=400, detail="Formato de vídeo não suportado.")

    unique_filename = f"{uuid4()}.{extension}"
    file_path = os.path.join(TMP_DIR, unique_filename)
    try:
        with open(file_path, "wb") as buffer:
            content = await upload_file.read()
            buffer.write(content)
        return file_path
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo: {e}")
        raise HTTPException(status_code=500, detail="Erro ao salvar o arquivo.")

# === 🧠 GERAÇÃO DE ROTEIRO ===

@router.post("/generate-script")
async def generate_script(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    try:
        data = await request.json()
        script_input = ScriptGenerationInput(**data)

        if not script_input.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt é obrigatório.")

        script = editor_service.generate_ai_script(script_input.prompt)
        return JSONResponse({"result": script})

    except ValidationError as e:
        logger.warning(f"Validação falhou: {e}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        logger.error(f"Erro inesperado ao gerar script: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar o roteiro.")

# === 🎥 PROCESSAMENTO DE VÍDEO COM IA ===

@router.post("/process-video")
async def process_video(
    video: UploadFile = File(...),
    enhancements: str = Form(...),
    seo: str = Form(...),
    resolution: str = Form(...),
    aspectRatio: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    try:
        video_input = VideoProcessingInput(
            enhancements=enhancements,
            seo=seo,
            resolution=resolution,
            aspectRatio=aspectRatio
        )

        enhancements_data = json.loads(video_input.enhancements)
        seo_data = json.loads(video_input.seo)

        if not video.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="Por favor, envie um arquivo de vídeo válido.")

        output_path = editor_service.save_temp_video(video)

        return {
            "message": "Vídeo processado com sucesso.",
            "video_url": f"{settings.BASE_URL}/{output_path}"
        }

    except json.JSONDecodeError:
        logger.warning("JSON inválido recebido em enhancements ou seo.")
        raise HTTPException(status_code=422, detail="JSON inválido em enhancements ou SEO.")
    except ValidationError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        logger.error(f"Erro inesperado ao processar vídeo: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar o vídeo.")

# === ✂️ CORTES SIMPLES ===

@router.post("/cut/")
async def cut_single_segment(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    start_time: float = Form(...),
    end_time: float = Form(...)
):

    if start_time >= end_time or start_time < 0 or end_time < 0:
        raise HTTPException(status_code=400, detail="Tempos de corte inválidos.")

    video_path = await save_upload_file(file)
    output_path = os.path.join(TMP_DIR, f"cut_{uuid4()}.mp4")
    success = apply_cut(video_path, start_time, end_time, output_path)

    background_tasks.add_task(os.remove, video_path)

    if success:
        return {"message": "Vídeo cortado com sucesso!", "output_path": output_path}
    else:
        raise HTTPException(status_code=500, detail="Erro ao cortar o vídeo.")

# === ✂️ CORTES MÚLTIPLOS ===

@router.post("/cut-multiple/")
async def cut_multiple_segments(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    cuts: str = Form(...)
):

    try:
        cuts_list = json.loads(cuts)
        if not isinstance(cuts_list, list):
            raise HTTPException(status_code=400, detail="Esperado uma lista de cortes.")

        for cut in cuts_list:
            if not isinstance(cut, dict) or 'start' not in cut or 'end' not in cut:
                raise HTTPException(status_code=400, detail="Formato de corte inválido.")
            if cut['start'] >= cut['end'] or cut['start'] < 0 or cut['end'] < 0:
                raise HTTPException(status_code=400, detail="Tempos inválidos em corte.")

        video_path = await save_upload_file(file)
        output_dir = os.path.join(TMP_DIR, f"cuts_{uuid4()}")
        cut_files = apply_multiple_cuts(video_path, cuts_list, output_dir)

        background_tasks.add_task(os.remove, video_path)

        if cut_files:
            return {"message": "Vídeo cortado com sucesso!", "output_paths": cut_files}
        else:
            raise HTTPException(status_code=500, detail="Erro ao cortar vídeo em múltiplos trechos.")

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato JSON inválido.")

# === 🔗 CONCATENAÇÃO ===

@router.post("/concatenate/")
async def concatenate_segments(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    files: List[UploadFile] = File(...)
):

    if not files or len(files) < 2:
        raise HTTPException(status_code=400, detail="Envie ao menos dois arquivos para concatenar.")

    input_paths = []
    try:
        for file in files:
            path = await save_upload_file(file)
            input_paths.append(path)

        output_path = os.path.join(TMP_DIR, f"concatenated_{uuid4()}.mp4")
        success = concatenate_video_segments(input_paths, output_path)

        if success:
            return {"message": "Vídeos concatenados com sucesso!", "output_path": output_path}
        else:
            raise HTTPException(status_code=500, detail="Erro ao concatenar vídeos.")

    except Exception as e:
        logger.error(f"Erro ao concatenar vídeos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao concatenar vídeos.")
    finally:
        for path in input_paths:
            if os.path.exists(path):
                background_tasks.add_task(os.remove, path)
