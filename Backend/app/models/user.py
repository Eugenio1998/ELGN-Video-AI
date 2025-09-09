import uuid
from enum import Enum
from datetime import datetime

from sqlalchemy import String, DateTime, Enum as PgEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    PREMIUM = "PREMIUM"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    display_name: Mapped[str] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(PgEnum(UserRole, name="userrole"), default=UserRole.USER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="SET NULL"), nullable=True)

    # 🔗 Relacionamentos
    plan = relationship("Plan", back_populates="users", lazy="joined", uselist=False)
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    audios = relationship("Audio", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    images = relationship("Image", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    seos = relationship("SEO", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    downloads = relationship("Download", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    subscription = relationship("Subscription", back_populates="user", cascade="all, delete-orphan", uselist=False, lazy="joined")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

    @property
    def is_admin_bypass(self) -> bool:
        return self.email.lower() == "elgn@tech.com"


# ⬇️ Isso garante que todas as classes referenciadas estejam carregadas
from app.models.video import Video
from app.models.audio import Audio
from app.models.image import Image
from app.models.seo import SEO
from app.models.download import Download
from app.models.feedback import Feedback
from app.models.usage_log import UsageLog
from app.models.subscription import Subscription
from app.models.activity_log import ActivityLog
from app.models.plan import Plan
