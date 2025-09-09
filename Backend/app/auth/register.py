# 📁 app/auth/register.py

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, constr, validator
from sqlalchemy.orm import Session
from pydantic import Field

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.hashing import hash_password
from app.models.plan import Plan

# === ⚙️ Configurações ===
logger = logging.getLogger(__name__)
router = APIRouter()

# === 📦 Schemas ===

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator('username')
    def username_must_be_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("O nome de usuário deve ser alfanumérico.")
        return v

class UserRegisterResponse(BaseModel):
    message: str
    username: str

# === 🧾 Rota de Registro de Usuário ===

@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Autenticação"]
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo usuário com validação de duplicidade de username e email.
    """

    errors = []

    if db.query(User).filter(User.username == user_data.username).first():
        errors.append({"field": "username", "msg": "Nome de usuário já existe."})

    if db.query(User).filter(User.email == user_data.email).first():
        errors.append({"field": "email", "msg": "Email já cadastrado."})

    if errors:
        logger.warning(f"❌ Registro bloqueado por duplicidade: {errors}")
        raise HTTPException(status_code=400, detail=errors)

    # 📌 Buscar plano gratuito
    free_plan = db.query(Plan).filter(Plan.name.ilike("free")).first()

    new_user = User(
    username=user_data.username,
    email=user_data.email,
    password=hash_password(user_data.password),
    created_at=datetime.utcnow(),
    role=UserRole.USER,
    plan=free_plan  # 🔐 Associar o plano gratuito
)



    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"✅ Novo usuário registrado: {new_user.username} ({new_user.email})")
        return {
            "message": "Usuário criado com sucesso.",
            "username": new_user.username
        }

    except Exception as e:
       db.rollback()
       print(f"🔥 Erro ao registrar usuário: {e}")  # 🔧 print adicional
       logger.error(f"🔥 Erro ao registrar usuário {user_data.username}: {e}")
       raise HTTPException(status_code=500, detail="Erro interno ao criar o usuário.")



