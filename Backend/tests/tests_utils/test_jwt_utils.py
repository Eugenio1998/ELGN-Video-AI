# 📁 app/utils/jwt.py

import os
from datetime import datetime, timedelta
from jose import jwt

def create_access_token(data: dict, expires_delta: int = 3600, secret_key: str = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    key = secret_key or os.getenv("SECRET_KEY")  # <-- agora permite injeção em teste
    encoded_jwt = jwt.encode(to_encode, key, algorithm="HS256")
    return encoded_jwt
