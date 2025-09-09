# 📁 backend/app/models/activity_log.py

from datetime import datetime
from sqlalchemy import String, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_user_timestamp", "user_id", "timestamp"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="activity_logs")
    
    def __repr__(self) -> str:
        return f"<ActivityLog(user_id={self.user_id}, action='{self.action}', timestamp={self.timestamp})>"
