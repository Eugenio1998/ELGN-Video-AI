# 📁 tests/tests_dependencies/test_auth.py

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.auth.jwt import create_access_token
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.plan import Plan
from app.database import get_db


@pytest.fixture(scope="function")
def db():
    """Fornece uma sessão de banco temporária para o teste."""
    yield from get_db()


@pytest.fixture(scope="function")
def test_user(db: Session):
    """Cria um usuário de teste no banco de dados."""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed123",
        plan=Plan(name="Pro"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()


def test_get_current_user_success(db: Session, test_user: User):
    """✅ Deve retornar usuário se token for válido."""
    token = create_access_token(data={"sub": test_user.username})
    user_from_token = get_current_user(token=token, db=db)
    assert user_from_token.username == test_user.username


def test_get_current_user_invalid_token(db: Session):
    """❌ Deve lançar erro se token for inválido."""
    with pytest.raises(HTTPException):
        get_current_user(token="invalid.token.value", db=db)


def test_get_current_user_nonexistent_user(db: Session):
    """❌ Deve lançar erro se usuário do token não existir no banco."""
    token = create_access_token(data={"sub": "nonexistentuser"})
    with pytest.raises(HTTPException):
        get_current_user(token=token, db=db)
