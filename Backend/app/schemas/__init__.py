# 📁 backend/app/schemas/__init__.py

# === 🔐 Autenticação ===
from .auth import Token, TokenData, TokenWithRefresh

# === 👤 Usuário ===
from .user import UserCreate, UserOut, UserRole

# === 📝 Feedbacks ===
from .feedback import FeedbackCreate, FeedbackOut, FeedbackCategory, FeedbackListOut

# === ✂️ Editor de vídeo ===
from .editor import CutRequest, MultipleCutRequest, CutResponse

# === 📼 Vídeos ===
from .video import VideoCreate, VideoOut, VideoListOut

__all__ = [
    "Token", "TokenData", "TokenWithRefresh",
    "UserCreate", "UserOut", "UserRole",
    "FeedbackCreate", "FeedbackOut", "FeedbackCategory", "FeedbackListOut",
    "CutRequest", "MultipleCutRequest", "CutResponse",
    "VideoCreate", "VideoOut", "VideoListOut",
]
