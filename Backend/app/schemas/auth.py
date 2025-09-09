# 📁 backend/app/schemas/auth.py

from pydantic import BaseModel, Field
from typing import Optional, Annotated


class Token(BaseModel):
    """Modelo de resposta para autenticação JWT."""

    access_token: Annotated[str, Field(min_length=1, example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")]
    token_type: Annotated[str, Field(min_length=1, example="bearer")]

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class TokenData(BaseModel):
    """Payload extraído do JWT após decodificação."""

    user_id: Optional[Annotated[int, Field(example=42)]] = None
    # exp: Optional[int] = Field(None, example=1716763462)
    # scope: Optional[str] = Field(None, example="admin")


class TokenWithRefresh(BaseModel):
    """Modelo de resposta com token de acesso e refresh token."""

    access_token: Annotated[str, Field(min_length=1, example="eyJh...")]
    refresh_token: Annotated[str, Field(min_length=1, example="dGhp...")]
    token_type: Annotated[str, Field(min_length=1, example="bearer")] = "bearer"
