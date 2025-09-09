# 📁 app/auth/login.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.hashing import verify_password
from app.auth.jwt import create_access_token
from app.api.error_response import ErrorResponse
import logging
from uuid import UUID
from pydantic import field_validator

# 🚀 Inicialização
router = APIRouter()
logger = logging.getLogger(__name__)

# 📦 Schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: str
    username: str
    role: str
    plan: str = "free"
    image_url: str | None = None

    @field_validator("user_id", mode="before")
    @classmethod
    def convert_user_id(cls, v):
        return str(v)

# 🔐 Endpoint de login
@router.post("/login", response_model=LoginResponse, responses={401: {"model": ErrorResponse}})
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password):
        logger.warning(f"❌ Falha de login para: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos."
        )

    # Cria o token JWT com ID do usuário
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
        "plan": user.plan.name if user.plan else "free",
    }
    access_token = create_access_token(data=token_data)

    logger.info(f"✅ Login realizado com sucesso para {user.username} ({user.email})")

    # Retorna os dados essenciais para o frontend
    return LoginResponse(
        token=access_token,
        user_id=str(user.id),
        username=user.username,
        role=user.role.value,
        plan=user.plan.name if user.plan else "free",
        image_url=user.avatar_url or "/img/user.png"
    )
