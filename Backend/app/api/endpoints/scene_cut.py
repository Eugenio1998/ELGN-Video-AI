# ✅ Rota de corte automático de cenas por IA

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from app.services.scene_cut_service import detect_scenes_and_cut
from pathlib import Path
import uuid
import shutil

router = APIRouter(prefix="/api/v1/scene-cut", tags=["Scene Cut"])

@router.post("/")
async def cortar_cenas_por_ia(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,  # ✅ Corrigido: colocar como default ou mover para fim
):
    try:
        # 📁 Diretório temporário de trabalho
        tmp_dir = Path("/tmp/scene_cut")
        tmp_dir.mkdir(parents=True, exist_ok=True)

        # 📥 Salvar o arquivo temporariamente
        file_id = uuid.uuid4().hex
        input_path = tmp_dir / f"{file_id}_{file.filename}"
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 📤 Diretório de saída
        output_dir = tmp_dir / f"{file_id}_cenas"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 🧠 Executar processamento em segundo plano
        if background_tasks:
            background_tasks.add_task(detect_scenes_and_cut, input_path, output_dir)
        else:
            detect_scenes_and_cut(input_path, output_dir)

        return JSONResponse(
            status_code=202,
            content={
                "message": "Corte por cenas iniciado com sucesso.",
                "file_id": file_id,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar vídeo: {str(e)}")
