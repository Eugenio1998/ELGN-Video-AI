import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Query, Depends

from api.deps import require_role
from app.models.user import UserRole
from app.core.config import settings  # ✅ centralização de configs

# === ⚙️ Configurações e setup ===
router = APIRouter()
logger = logging.getLogger(__name__)

PROCESSED_DIR = settings.PROCESSED_DIR or "processed_videos/"
FAILED_DIR = settings.FAILED_DIR or "failed_videos/"
PROCESS_LOG = settings.PROCESS_LOG or "logs/process_times.json"

# Garante existência dos diretórios
for path in [PROCESSED_DIR, FAILED_DIR, os.path.dirname(PROCESS_LOG)]:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logger.warning(f"⚠️ Erro ao criar diretório {path}: {e}")


# === 📊 Estatísticas Administrativas ===
@router.get("/stats", dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_admin_stats(
    days: int = Query(7, ge=1, le=90, description="Número de dias anteriores para analisar estatísticas")
) -> Dict[str, Any]:
    """
    📊 Estatísticas administrativas:
    - Total de vídeos processados
    - Taxa de sucesso e falha
    - Tempo médio de processamento
    - Histórico diário de uploads
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    total_videos = 0
    failed_videos = 0
    success_videos = 0
    process_times: List[float] = []
    history: Dict[str, int] = {}

    # === 📁 Contagem de arquivos
    for folder, status in [(PROCESSED_DIR, "completed"), (FAILED_DIR, "failed")]:
        if not os.path.exists(folder):
            continue

        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if creation_time >= start_date:
                    total_videos += 1
                    date_str = creation_time.date().isoformat()
                    history[date_str] = history.get(date_str, 0) + 1
                    if status == "completed":
                        success_videos += 1
                    else:
                        failed_videos += 1
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar arquivo {file_path}: {e}")

    # === 🕒 Log de tempo de processamento
    if os.path.exists(PROCESS_LOG):
        try:
            with open(PROCESS_LOG, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    try:
                        timestamp = datetime.strptime(item.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
                        if timestamp >= start_date:
                            process_times.append(float(item.get("duration", 0)))
                    except Exception as e:
                        logger.error(f"❌ Erro ao processar log: {item} — {e}")
        except Exception as e:
            logger.error(f"❌ Erro ao abrir log de tempos: {e}")

    # === 📈 Estatísticas finais
    success_rate = (success_videos / total_videos * 100) if total_videos else 0.0
    failure_rate = (failed_videos / total_videos * 100) if total_videos else 0.0
    average_time = sum(process_times) / len(process_times) if process_times else 0.0

    return {
        "total_videos": total_videos,
        "success_rate": round(success_rate, 2),
        "failure_rate": round(failure_rate, 2),
        "average_processing_time": round(average_time, 2),
        "history": [{"date": date, "count": count} for date, count in sorted(history.items())],
    }
