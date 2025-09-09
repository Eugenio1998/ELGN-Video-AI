# 📁 app/config.py

from typing import List, Optional
from pydantic import Field, ValidationError, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# === 🔐 Carrega variáveis de ambiente ===
load_dotenv(".env", override=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # === 🧠 App ===
    app_name: str = "ELGN Video.AI"
    pythonpath: str = "./backend/app"

    # === 🔐 Segurança ===
    secret_key: str
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # === 💾 Banco de Dados ===
    database_url: str = Field(..., env="DATABASE_URL")

    # === 💳 Stripe ===
    stripe_secret_key: str

    # === 🤖 OpenAI ===
    openai_api_key: str

    # === ⚙️ Celery & Redis ===
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    redis_url: str = "redis://redis:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # === 📁 Diretórios ===
    UPLOAD_FOLDER: str = "uploads"
    TMP_DIR: str = Field("/tmp", env="TMP_DIR")
    log_dir: str = "logs"
    backup_dir: str = "logs_backup"

    # === 📧 E-mail (opcional para evitar erro de boot)
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_user: Optional[str] = None
    email_pass: Optional[str] = None
    email_sender: Optional[str] = None
    email_receiver: Optional[str] = None
    admin_emails: List[str] = Field(default_factory=list)

    # === 🔗 API
    API_V1_STR: str = "/api/v1"

    # === 🌍 CORS
    allowed_origins: List[AnyHttpUrl] = Field(
        default_factory=lambda: ["http://localhost", "http://localhost:3000"]
    )

try:
    settings = Settings()
except ValidationError as e:
    import sys
    print("\n❌ Falha ao carregar configurações. Verifique o arquivo .env:")
    print(e)
    sys.exit(1)
