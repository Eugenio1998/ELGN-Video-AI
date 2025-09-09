# 📄 tests/tests_schemas/test_user_schemas.py

from app.schemas.user import UserCreate, UserOut, UserRole
from datetime import datetime

def test_user_create_schema():
    user = UserCreate(username="elgn_user", email="elgn@ai.com", password="12345678")
    assert user.username == "elgn_user"
    assert user.password == "12345678"

def test_user_out_schema():
    now = datetime.utcnow()
    user = UserOut(
        id=1,
        username="elgn_user",
        email="elgn@ai.com",
        created_at=now,
        updated_at=now,
        role=UserRole.USER,
        is_active=True
    )
    assert user.role == "user"
    assert user.is_active is True
