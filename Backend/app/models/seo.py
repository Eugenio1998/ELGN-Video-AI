# 📁 backend/app/models/seo.py

from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base

# 🧠 Entradas de SEO geradas por IA ou usuário
class SEO(Base):
    __tablename__ = "seos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    video_title: Mapped[str] = mapped_column(String(255), nullable=False)
    video_description: Mapped[str] = mapped_column(String(1024), nullable=True)
    keywords: Mapped[str] = mapped_column(String(512), nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    user = relationship("User", back_populates="seos", lazy="selectin")

    def __repr__(self):
        return f"<SEO id={self.id} user_id={self.user_id} language={self.language}>"
