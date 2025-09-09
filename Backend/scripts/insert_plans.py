# scripts/insert_plans.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.models import Plan, Base

# === 🔐 Carrega variáveis do .env
load_dotenv()

# === 📦 Configuração da conexão
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# === 🎯 Lista de planos
plans_data = [
    {"name": "Basic", "price": 10, "features": "Acesso parcial. Sem nuvem. Máx 5 downloads", "storage_gb": 0, "max_downloads": 5},
    {"name": "Pro", "price": 25, "features": "2/3 dos recursos + 100GB nuvem", "storage_gb": 100, "max_downloads": None},
    {"name": "Premium", "price": 50, "features": "Todos os recursos + 500GB nuvem", "storage_gb": 500, "max_downloads": None},
    {"name": "Empresarial", "price": 100, "features": "Acesso total + 1TB nuvem", "storage_gb": 1000, "max_downloads": None},
    {"name": "Basic Anual", "price": 100, "features": "Acesso parcial anual. Sem nuvem. Máx 5 downloads", "storage_gb": 0, "max_downloads": 5},
    {"name": "Pro Anual", "price": 250, "features": "2/3 recursos anuais + 200GB nuvem", "storage_gb": 200, "max_downloads": None},
    {"name": "Premium Anual", "price": 500, "features": "Recursos completos anuais + 1TB nuvem", "storage_gb": 1000, "max_downloads": None},
    {"name": "Empresarial Anual", "price": 1000, "features": "Acesso total anual + 2TB nuvem", "storage_gb": 2000, "max_downloads": None},
]

# === 🚀 Execução
def main():
    session = SessionLocal()
    try:
        for data in plans_data:
            exists = session.query(Plan).filter_by(name=data["name"]).first()
            if not exists:
                plan = Plan(**data)
                session.add(plan)
        session.commit()
        print("✅ Planos inseridos com sucesso!")
    except Exception as e:
        session.rollback()
        print("❌ Erro ao inserir planos:", e)
    finally:
        session.close()

if __name__ == "__main__":
    main()
