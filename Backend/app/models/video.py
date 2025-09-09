from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid
from sqlalchemy import Integer, Column
from app.database import Base

# 📼 Modelo de Vídeo Processado
class Video(Base):
    __tablename__ = "videos"
    __table_args__ = (
        Index("ix_video_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(120), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    video_url: Mapped[str] = mapped_column(String(255), nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String, default="pending")

    size: Mapped[int] = mapped_column(Integer, default=0)  

    user = relationship("User", back_populates="videos", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Video id={self.id} user_id={self.user_id}>"
