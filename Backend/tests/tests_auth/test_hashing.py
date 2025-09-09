# ✅ tests/tests_auth/test_hashing.py

from app.auth.hashing import hash_password, verify_password


def test_password_hash_and_verify():
    senha = "minhaSenhaSegura123"
    hash_gerado = hash_password(senha)

    assert verify_password(senha, hash_gerado) is True
    assert verify_password("senhaErrada", hash_gerado) is False
