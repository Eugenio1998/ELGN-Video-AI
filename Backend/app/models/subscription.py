# 📁 backend/app/models/subscription.py

from sqlalchemy import String, Integer, ForeignKey, Enum, Index, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from datetime import date
import enum
from app.enums import PaymentStatusEnum

# 📦 Status de pagamento da assinatura
class PaymentStatusEnum(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CANCELED = "canceled"

# 🧾 Modelo de Assinatura
class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        Index("ix_subscription_status_due", "payment_status", "next_payment_due"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id"), nullable=False)
    
    payment_status: Mapped[PaymentStatusEnum] = mapped_column(
        default=PaymentStatusEnum.PENDING,
        nullable=False
    )    
    last_payment_date: Mapped[date] = mapped_column(Date, nullable=True)
    next_payment_due: Mapped[date] = mapped_column(Date, nullable=True)

    user = relationship("User", back_populates="subscription", lazy="joined")
    plan = relationship("Plan", back_populates="subscriptions", lazy="joined")

    def __repr__(self):
        return (
            f"<Subscription user_id={self.user_id} "
            f"plan={self.plan.name if self.plan else 'N/A'} "
            f"status={self.payment_status.value}>"
        )
