# 📁 backend/app/models/feedback.py

from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, Text, Enum, Index, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import enum

# 🎯 Categorias disponíveis para feedback
class FeedbackCategory(enum.Enum):
    VIDEO = "video"
    VOICE = "voice"
    APP = "app"
    SUGESTAO = "sugestao"

class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        Index("ix_feedback_category_created_at", "category", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    category: Mapped[FeedbackCategory] = mapped_column(
        Enum(FeedbackCategory, name="feedbackcategory"),
        default=FeedbackCategory.APP,
        nullable=False
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="feedbacks", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<Feedback id={self.id} user_id={self.user_id} "
            f"category={self.category.value} created_at={self.created_at}>"
        )
