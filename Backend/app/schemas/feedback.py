# 📁 backend/app/schemas/feedback.py

from pydantic import BaseModel, Field, model_validator
from typing import Annotated, List, Any
from datetime import datetime
from enum import Enum


# === Enum para categorias de feedback ===
class FeedbackCategory(str, Enum):
    """Categorias disponíveis para envio de feedback."""
    VIDEO = "video"
    VOICE = "voice"
    APP = "app"
    SUGESTAO = "sugestao"


# === Requisição de criação de feedback ===
class FeedbackCreate(BaseModel):
    """Modelo de entrada para envio de feedback."""

    category: Annotated[FeedbackCategory, Field(description="Categoria do feedback", example="app")]
    message: Annotated[str, Field(min_length=3, max_length=1000, description="Mensagem enviada pelo usuário", example="Gostaria de sugerir uma nova funcionalidade...")]

    @model_validator(mode="before")
    @classmethod
    def check_min_length_for_sugestao(cls, values: dict[str, Any]) -> dict[str, Any]:
        category = values.get("category")
        message = values.get("message", "")
        if category == FeedbackCategory.SUGESTAO and len(message) < 10:
            raise ValueError("Sugestões devem conter pelo menos 10 caracteres.")
        return values


# === Resposta única de feedback ===
class FeedbackOut(BaseModel):
    """Modelo de saída de feedback individual."""

    id: Annotated[int, Field(title="ID do feedback", example=1)]
    user_id: Annotated[int, Field(title="ID do usuário", example=42)]
    category: Annotated[FeedbackCategory, Field(title="Categoria", example="voice")]
    message: Annotated[str, Field(title="Mensagem", example="Áudio ficou com atraso...")]
    created_at: Annotated[datetime, Field(title="Data de envio")]

    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }


# === Lista de feedbacks para listagem em batch ===
FeedbackListOut = List[FeedbackOut]
