from app.auth.jwt import create_access_token, decode_access_token

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

def test_create_and_decode_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "testuser"