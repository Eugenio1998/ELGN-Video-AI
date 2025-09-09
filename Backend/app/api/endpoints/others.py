# 📁 backend/app/api/endpoints/others.py

import logging
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel

from app.tasks import analyze_sentiment_task
from app.api.error_response import ErrorResponse

router = APIRouter(prefix="/analysis")
logger = logging.getLogger(__name__)

# === 🧠 Schema de Resposta ===

class SentimentTaskResponse(BaseModel):
    task_id: str
    message: str

# === 📊 Endpoint: Análise de Sentimento ===

@router.post(
    "/sentiment",
    response_model=SentimentTaskResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["Análise"]
)
async def analyze_text_sentiment(
    text: str = Form(..., min_length=5, max_length=1000, description="Texto para análise de sentimento")
):
    """
    Inicia uma task Celery assíncrona para análise de sentimento do texto fornecido.
    """
    try:
        task = analyze_sentiment_task.delay(text)
        logger.info(f"📈 Análise de sentimento iniciada | Task ID: {task.id}")
        return SentimentTaskResponse(
            task_id=task.id,
            message="Análise de sentimento iniciada com sucesso."
        )
    except Exception as e:
        logger.exception(f"Erro ao iniciar análise de sentimento: {e}")
        raise HTTPException(status_code=500, detail="Erro ao iniciar a análise de sentimento.")
