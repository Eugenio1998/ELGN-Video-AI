# 📁 app/database.py

import os
import logging
from dotenv import load_dotenv

# === 📥 Carrega variáveis de ambiente (.env ou .env.test) ===
load_dotenv(".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from .config import settings

# === 📋 Logger ===
logger = logging.getLogger(__name__)

# === 🧱 Base de modelos SQLAlchemy ===
Base = declarative_base()

# === 🔗 URL do banco de dados ===
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL não definida. Verifique seu .env ou .env.test.")

# === ⚙️ Criação do engine com tratamento para SQLite ===
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# === 📦 Sessão de banco de dados (scoped para threads) ===
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# === 🔁 Dependência do FastAPI para obter sessão ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === 🧪 Teste de conexão com o banco ===
def test_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Conexão com o banco de dados bem-sucedida.")
        return True
    except Exception as e:
        logger.error(f"❌ Erro na conexão com o banco de dados: {e}")
        return False

# === 🛠️ Inicializa/cria tabelas (dev/teste) ===
def init_db() -> None:
    try:
        import app.models
        Base.metadata.create_all(bind=engine)
        logger.info("📦 Tabelas criadas com sucesso no banco de dados.")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
