# 📄 tests/tests_schemas/test_auth_schemas.py

from app.schemas.auth import Token, TokenData, TokenWithRefresh

def test_token_schema():
    token = Token(access_token="abc123", token_type="bearer")
    assert token.access_token == "abc123"
    assert token.token_type == "bearer"

def test_token_data_optional():
    data = TokenData()
    assert data.user_id is None

def test_token_with_refresh_schema():
    token = TokenWithRefresh(
        access_token="abc123",
        refresh_token="xyz789",
        token_type="bearer"
    )
    assert token.refresh_token == "xyz789"
