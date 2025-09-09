# ✅ tests/tests_auth/test_utils.py

from app.auth.utils import generate_otp, validate_otp, redis_conn


def test_generate_and_validate_otp():
    username = "teste_usuario"
    codigo = generate_otp(username)

    assert len(codigo) == 6
    assert validate_otp(username, codigo) is True
    # Segunda tentativa deve falhar (código já foi usado e apagado)
    assert validate_otp(username, codigo) is False
