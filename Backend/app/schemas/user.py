# 📁 backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Annotated
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Define os papéis disponíveis para usuários do sistema."""
    USER = "user"
    ADMIN = "admin"
    MANAGER = "manager"


class UserBase(BaseModel):
    """Campos básicos de entrada e saída para usuários."""

    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            pattern=r"^[a-zA-Z0-9_]+$",
            description="Nome de usuário. Apenas letras, números e underline.",
            example="elgn_user"
        )
    ]
    email: Annotated[
        EmailStr,
        Field(
            description="Endereço de e-mail válido.",
            example="user@elgn.ai"
        )
    ]

    model_config = {
        "from_attributes": True
    }


class UserCreate(UserBase):
    """Modelo de entrada para criação de novo usuário."""

    password: Annotated[
        str,
        Field(
            min_length=8,
            max_length=128,
            description="Senha com no mínimo 8 caracteres.",
            example="12345678"
        )
    ]

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    """Modelo para atualização de perfil de usuário."""

    username: Annotated[
        Optional[str],
        Field(
            min_length=3,
            max_length=50,
            pattern=r"^[a-zA-Z0-9_]+$",
            description="Nome de usuário atualizado",
            example="novo_nome"
        )
    ] = None

    email: Annotated[
        Optional[EmailStr],
        Field(
            description="Novo e-mail do usuário",
            example="novo@elgn.ai"
        )
    ] = None

    password: Annotated[
        Optional[str],
        Field(
            min_length=8,
            max_length=128,
            description="Nova senha com no mínimo 8 caracteres"
        )
    ] = None

    role: Annotated[
        Optional[UserRole],
        Field(description="Função do usuário (admin, user, manager)", example="user")
    ] = None

    is_active: Annotated[
        Optional[bool],
        Field(description="Status de ativação do usuário")
    ] = None

    model_config = {
        "from_attributes": True
    }


class UserOut(UserBase):
    """Modelo de saída com dados públicos e administrativos do usuário."""

    id: Annotated[int, Field(description="ID do usuário", example=1)]
    created_at: Annotated[datetime, Field(description="Data de criação", example="2025-05-01T12:00:00Z")]
    updated_at: Annotated[datetime, Field(description="Data da última atualização", example="2025-05-15T14:30:00Z")]
    role: Annotated[UserRole, Field(description="Papel do usuário", example="user")]
    is_active: Annotated[bool, Field(description="Status do usuário", example=True)]

    model_config = {
        "from_attributes": True
    }
