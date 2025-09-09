# 📁 backend/app/models/image.py

from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Integer, Column

class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    resolution: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    size: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship("User", back_populates="images", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Image id={self.id} user_id={self.user_id} resolution={self.resolution}>"
