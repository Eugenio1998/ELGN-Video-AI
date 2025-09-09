# app/startup.py

from sqlalchemy import create_engine
from app.models import Base
from app.config import settings

def init_db():
    """Cria todas as tabelas do banco de dados."""
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
