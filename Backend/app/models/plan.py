# 📁 backend/app/models/plan.py

from sqlalchemy import String, Float, Boolean, Integer, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base

# 🧾 Modelo de Plano (Free, Basic, Pro, Premium etc.)
class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = (
        Index("ix_plan_active_price", "is_active", "price"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    max_video_duration: Mapped[int] = mapped_column(Integer, nullable=True)

    subscriptions = relationship("Subscription", back_populates="plan", lazy="selectin")
    users = relationship("User", back_populates="plan", lazy="selectin")


    def __repr__(self) -> str:
        return f"<Plan id={self.id} name='{self.name}' price={self.price:.2f} active={self.is_active}>"
