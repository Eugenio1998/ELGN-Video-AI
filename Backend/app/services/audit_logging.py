# 🧾 Registro Centralizado de Auditoria

import os
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.models.user import User

# === 📁 Configuração de Diretório de Logs ===
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "audit.log")

# === 🛠 Logger de Auditoria ===
audit_logger = logging.getLogger("audit_logger")
audit_logger.setLevel(logging.INFO)

# Evita duplicação de handlers ao recarregar
if not any(isinstance(h, logging.FileHandler) and h.baseFilename == LOG_FILE for h in audit_logger.handlers):
    file_handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    audit_logger.addHandler(file_handler)

# === 🔎 Utilitário: Pega nome do usuário por ID ===
def get_username_by_id(user_id: int, db: Session) -> str:
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user.username if user else f"Desconhecido (ID: {user_id})"
    except Exception:
        return f"ErroUsuario (ID: {user_id})"

# === 🧾 Log Centralizado ===
def log_event(user_id: int, action: str, db: Session) -> dict:
    try:
        username = get_username_by_id(user_id, db)
        audit_logger.info(f"👤 Usuário: {username} (ID: {user_id}) - 📝 Ação: {action}")
        return {"message": "🔍 Evento registrado com sucesso."}
    except Exception as e:
        audit_logger.error(f"❌ Erro ao registrar evento | ID: {user_id} | Ação: {action} | Erro: {e}")
        return {"message": "Erro ao registrar evento de auditoria."}

# === 🔐 Ações de Login ===
def log_user_login(user_id: int, db: Session) -> dict:
    return log_event(user_id, "Login realizado", db)

def log_user_logout(user_id: int, db: Session) -> dict:
    return log_event(user_id, "Logout realizado", db)

# === 🎞️ Ações com Vídeos ===
def log_video_upload(user_id: int, db: Session) -> dict:
    return log_event(user_id, "Upload de vídeo", db)

def log_video_processed(user_id: int, video_filename: str, db: Session) -> dict:
    return log_event(user_id, f"Vídeo processado: {video_filename}", db)

def log_video_processing_failed(user_id: int, video_filename: str, error: str, db: Session) -> dict:
    audit_logger.error(
        f"❌ Falha no processamento | Usuário ID: {user_id} | Vídeo: {video_filename} | Erro: {error}"
    )
    return {"message": "⚠️ Falha no processamento registrada."}

# === 💳 Ações com Pagamentos ===
def log_payment(user_id: int, status: str, db: Session) -> dict:
    return log_event(user_id, f"Pagamento {status}", db)

# === 👤 Registro e Exclusão de Usuário ===
def log_user_registration(user_id: int, username: str, email: str, db: Session) -> dict:
    audit_logger.info(f"🆕 Novo usuário | Username: {username} | Email: {email} | ID: {user_id}")
    return {"message": "Registro de novo usuário logado."}

def log_user_deletion(user_id: int, username: str, db: Session) -> dict:
    audit_logger.warning(f"🗑️ Usuário deletado | Username: {username} | ID: {user_id}")
    return {"message": "Deleção de usuário logada."}

# === ⚙️ Ações Administrativas ===
def log_admin_action(admin_id: int, action: str, details: str = "", db: Session = Depends(get_db)) -> dict:
    try:
        username = get_username_by_id(admin_id, db)
        audit_logger.warning(f"⚙️ Admin: {username} (ID: {admin_id}) - Ação: {action} | Detalhes: {details}")
        return {"message": "Ação administrativa registrada."}
    except Exception as e:
        audit_logger.error(f"❌ Erro ao registrar ação administrativa | ID: {admin_id} | Ação: {action} | Erro: {e}")
        return {"message": "Erro ao registrar ação administrativa."}
