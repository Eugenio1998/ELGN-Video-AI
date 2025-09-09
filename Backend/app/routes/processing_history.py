import os
import csv
import io
import logging
from collections import defaultdict
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Response, Depends
from fastapi.responses import JSONResponse

from api.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter(tags=["Admin"])
logger = logging.getLogger(__name__)

PROCESSED_DIR = os.getenv("PROCESSED_VIDEOS_DIR", "processed_videos")

def export_to_csv(data: dict) -> Response:
    """📤 Exporta histórico de vídeos processados em CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data", "Total Processado"])

    for date in sorted(data):
        writer.writerow([date, data[date]])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=historico_processamento.csv"
    response.headers["Cache-Control"] = "no-cache"
    return response


@router.get("/processing-history", dependencies=[Depends(require_role(UserRole.ADMIN))])
def get_processing_history(
    export_format: Literal["json", "csv"] = Query("json", description="Formato de exportação"),
    current_user: User = Depends(get_current_user)
):
    """
    📊 Retorna histórico de vídeos processados por data.
    🔒 Apenas administradores.
    """
    if not os.path.exists(PROCESSED_DIR):
        raise HTTPException(status_code=404, detail="Diretório de vídeos processados não encontrado.")

    history = defaultdict(int)

    try:
        for entry in os.scandir(PROCESSED_DIR):
            if entry.is_file():
                date_str = datetime.fromtimestamp(entry.stat().st_ctime).strftime("%Y-%m-%d")
                history[date_str] += 1

        if export_format == "csv":
            return export_to_csv(history)

        sorted_dates = sorted(history)
        counts = [history[date] for date in sorted_dates]

        return JSONResponse(
            status_code=200,
            content={
                "dates": sorted_dates,
                "counts": counts
            }
        )

    except Exception as e:
        logger.error(f"❌ Erro ao gerar histórico de processamento - ADMIN {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar histórico: {str(e)}")
