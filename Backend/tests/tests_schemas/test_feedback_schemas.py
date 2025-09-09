# 📄 tests/tests_schemas/test_feedback_schemas.py

from app.schemas.feedback import FeedbackCreate, FeedbackCategory, FeedbackOut
from datetime import datetime
import pytest

def test_feedback_create_valid():
    feedback = FeedbackCreate(category="app", message="Excelente recurso.")
    assert feedback.category == FeedbackCategory.APP

def test_feedback_create_sugestao_valida():
    feedback = FeedbackCreate(category="sugestao", message="Adicionar função X seria ótimo.")
    assert feedback.message.startswith("Adicionar")

def test_feedback_create_sugestao_curta():
    with pytest.raises(ValueError):
        FeedbackCreate(category="sugestao", message="Muito bom")

def test_feedback_out():
    feedback = FeedbackOut(
        id=1,
        user_id=2,
        category="video",
        message="Tudo certo",
        created_at=datetime.utcnow()
    )
    assert feedback.id == 1
