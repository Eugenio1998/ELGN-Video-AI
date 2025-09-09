# 📁 app/models/__init__.py

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# === 👤 Usuários e acesso ===
from .user import User, UserRole
from .plan import Plan
from .subscription import Subscription
from .payment import Payment

# === 📦 Conteúdo gerado ===
from .video import Video
from .audio import Audio
from .image import Image
from .seo import SEO

# === 📝 Feedbacks e logs ===
from .feedback import Feedback
from .activity_log import ActivityLog
from .usage_log import UsageLog
from .download import Download

__all__ = [
    "Base",
    "User", "UserRole",
    "Plan", "Subscription", "Payment",
    "Video", "Audio", "Image", "SEO",
    "Feedback", "ActivityLog", "UsageLog", "Download",
]