# 📁 backend/app/models/download.py

from datetime import datetime
from sqlalchemy import Integer, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base

class Download(Base):
    __tablename__ = "downloads"
    __table_args__ = (
        CheckConstraint(
            "(video_id IS NOT NULL)::int + (audio_id IS NOT NULL)::int + (image_id IS NOT NULL)::int = 1",
            name="only_one_media_per_download"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.id"), nullable=True)
    audio_id: Mapped[int] = mapped_column(Integer, ForeignKey("audios.id"), nullable=True)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="downloads", lazy="selectin")
    
    def __repr__(self) -> str:
        return (
            f"<Download id={self.id} user_id={self.user_id} "
            f"video={self.video_id} audio={self.audio_id} image={self.image_id}>"
        )
