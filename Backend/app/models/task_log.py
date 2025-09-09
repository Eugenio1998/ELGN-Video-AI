# 📁 backend/app/models/task_log.py

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class TaskLog(Base):
    """
    📊 Modelo de Log de Tarefas Celery e IA executadas no sistema.
    """
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(255), nullable=False, index=True, doc="Nome da tarefa (ex: video_process, generate_voice)")
    user_id = Column(Integer, nullable=True, doc="ID do usuário associado, se aplicável")
    status = Column(String(50), nullable=False, default="pending", doc="Status atual da tarefa (pending, success, failed)")
    message = Column(Text, nullable=True, doc="Mensagem adicional ou erro ocorrido na execução")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), doc="Data e hora de criação do log")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), doc="Data da última atualização")

    def __repr__(self):
        return f"<TaskLog(id={self.id}, task_name='{self.task_name}', status='{self.status}')>"
