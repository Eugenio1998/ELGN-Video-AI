# 📁 scripts/create_user.py
import sys
import os

# Adiciona o caminho raiz do projeto para importar corretamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, UserRole
from app.core.security import get_password_hash

# Cria a sessão
db = SessionLocal()

# Verifica se o usuário já existe
email_admin = "admin@elgn.ai"
user_existente = db.query(User).filter(User.email == email_admin).first()

if user_existente:
    print(f"⚠️ Usuário com email '{email_admin}' já existe: {user_existente.username}")
else:
    # Cria novo usuário admin
    novo_user = User(
        username="Admin",
        email=email_admin,
        hashed_password=get_password_hash("senha123"),
        is_active=True,
        is_superuser=True,
        role=UserRole.ADMIN  # ✅ define como admin
    )

    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)

    print(f"✅ Usuário admin criado com sucesso: {novo_user.email}")

# Encerra sessão
db.close()
