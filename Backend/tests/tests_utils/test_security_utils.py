from app.utils import generate_token

def test_generate_token_length():
    token = generate_token(16)
    assert len(token) == 16
