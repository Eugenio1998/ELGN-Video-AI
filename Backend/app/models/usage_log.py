# 📁 backend/app/models/usage_log.py

from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base

# 📊 Log de uso de funcionalidades
class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    detail: Mapped[str] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    user = relationship("User", back_populates="usage_logs", lazy="selectin")

    def __repr__(self):
        return (
            f"<UsageLog id={self.id} user_id={self.user_id} "
            f"resource_type={self.resource_type} quantity={self.quantity}>"
        )
