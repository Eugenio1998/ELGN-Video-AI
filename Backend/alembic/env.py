from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# === 🔐 Carrega variáveis do .env
load_dotenv()

# === 🧠 Adiciona caminho da pasta app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# === 📦 Importa os modelos e metadata
import app.models  # garante o registro de todos os modelos com o Base
from app.database import Base  # Base oficial do SQLAlchemy

# === 🌐 Lê a DATABASE_URL diretamente
DATABASE_URL = os.environ.get("DATABASE_URL")

# === ⚙️ Config Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
