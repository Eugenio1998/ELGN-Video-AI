import logging
from enum import Enum
from typing import List
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.services.feedback_service import store_feedback, get_feedback_by_user
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.api.error_response import ErrorResponse
from app.utils.exceptions import raise_error

router = APIRouter(tags=["Feedback"])
logger = logging.getLogger(__name__)

# === ENUM CONTEXTUAL ===

class FeedbackContext(str, Enum):
    general = "general"
    video = "video"
    voice = "voice"
    filter = "filter"

# === SCHEMAS ===

class FeedbackResponse(BaseModel):
    message: str

class FeedbackItem(BaseModel):
    context: FeedbackContext
    message: str
    created_at: str  # ISO 8601 format (ex: 2025-06-09T15:00:00Z)

# === ROTAS ===

@router.post(
    "/submit",
    response_model=FeedbackResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
)
def submit_feedback(
    message: str = Form(...),
    context: FeedbackContext = Form(FeedbackContext.general),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Envia um feedback com contexto (ex: vídeo, voz).
    """
    if len(message.strip()) < 3:
        raise_error(
            "Feedback muito curto.",
            status_code=400,
            error_type="validation_error",
            field="message"
        )

    try:
        store_feedback(current_user.id, message, context.value)
        logger.info(f"Feedback registrado de {current_user.username} no contexto '{context.value}'")
        return {"message": "Feedback enviado com sucesso!"}
    except Exception as e:
        logger.error(f"Erro ao armazenar feedback do usuário {current_user.id}: {e}")
        raise_error("Erro ao salvar o feedback.", status_code=500, error_type="processing_error")


@router.get(
    "/my-feedback",
    response_model=List[FeedbackItem],
    responses={401: {"model": ErrorResponse}},
)
def my_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os feedbacks enviados pelo usuário autenticado.
    """
    try:
        feedbacks = get_feedback_by_user(current_user.id)
        logger.info(f"Usuário {current_user.username} consultou seus feedbacks.")
        return feedbacks
    except Exception as e:
        logger.error(f"Erro ao buscar feedbacks do usuário {current_user.id}: {e}")
        raise_error("Erro ao buscar feedbacks.", status_code=500, error_type="processing_error")
