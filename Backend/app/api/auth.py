import os
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User
from app.models.user import UserRole
from app.api.error_response import ErrorResponse

# === Configurações ===
router = APIRouter(prefix="/auth", tags=["Autenticação"])
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "elgn_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# === Schemas ===

class UserCreate(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    full_name: constr(min_length=3, max_length=120)
    password: constr(min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# === Funções internas ===

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido.")
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return user

# === Endpoint: Registro ===

@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    username = data.username.lower()
    email = data.email.lower()

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Nome de usuário já existe.")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado.")


    new_user = User(
    email=email,
    username=username,
    full_name=data.full_name,
    hashed_password=hash_password(data.password),
    role=UserRole.USER,
    is_active=True,
    is_admin=False,
    created_at=datetime.utcnow()
)

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"✅ Usuário registrado: {new_user.username} ({new_user.email})")
        return new_user
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao registrar usuário {username}: {e}")
        raise HTTPException(status_code=500, detail="Erro ao registrar o usuário.")

# === Endpoint: Login ===

@router.post(
    "/login",
    response_model=TokenResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        logger.warning(f"⚠️ Falha de login: {data.username}")
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    try:
        token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        logger.info(f"🔓 Login bem-sucedido: {user.username} (ID: {user.id})")
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"❌ Erro ao gerar token: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar token de acesso.")

# === Endpoint: Perfil ===

@router.get(
    "/me",
    response_model=UserOut,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
