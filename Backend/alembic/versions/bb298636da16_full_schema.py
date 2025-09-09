# 📁 alembic/versions/<timestamp>_full_schema.py

"""full schema"""

from alembic import op
import sqlalchemy as sa
import enum
from sqlalchemy.dialects import postgresql

# === 🔁 Revisão ===
revision = "full_schema_0001"
down_revision = None
branch_labels = None
depends_on = None

# === 🧩 Enums ===
class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    PREMIUM = "PREMIUM"

class FeedbackCategory(enum.Enum):
    VIDEO = "video"
    VOICE = "voice"
    APP = "app"
    SUGESTAO = "sugestao"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CANCELED = "canceled"

class PaymentStatus2(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

# === ⬆️ Upgrade ===
def upgrade():
    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("max_video_duration", sa.Integer, nullable=True),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("full_name", sa.String, nullable=True),
        sa.Column("display_name", sa.String, nullable=True),
        sa.Column("avatar_url", sa.String, nullable=True),
        sa.Column("role", sa.Enum(UserRole, name="userrole"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("username", sa.String(100), nullable=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id", ondelete="SET NULL"), nullable=True),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("payment_status", sa.Enum(PaymentStatus, name="paymentstatusenum"), nullable=False),
        sa.Column("last_payment_date", sa.Date, nullable=True),
        sa.Column("next_payment_due", sa.Date, nullable=True),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("status", sa.Enum(PaymentStatus2, name="paymentstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "videos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(120), nullable=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("video_url", sa.String(255), nullable=True),
        sa.Column("thumbnail_url", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_index("ix_video_user_created", "videos", ["user_id", "created_at"])

    op.create_table(
        "audios",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(120), nullable=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("audio_url", sa.String(2048), nullable=True),
        sa.Column("duration", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "images",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("prompt", sa.String(500), nullable=True),
        sa.Column("image_url", sa.String(2048), nullable=False),
        sa.Column("resolution", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "seos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("video_title", sa.String(255), nullable=False),
        sa.Column("video_description", sa.String(1024), nullable=True),
        sa.Column("keywords", sa.String(512), nullable=True),
        sa.Column("language", sa.String(10), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category", sa.Enum(FeedbackCategory, name="feedbackcategory"), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "downloads",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("video_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("videos.id"), nullable=True),
        sa.Column("audio_id", sa.Integer, sa.ForeignKey("audios.id"), nullable=True),
        sa.Column("image_id", sa.Integer, sa.ForeignKey("images.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "usage_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("detail", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "task_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("task_name", sa.String(255), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

# === ⬇️ Downgrade ===
def downgrade():
    op.drop_table("task_logs")
    op.drop_table("activity_logs")
    op.drop_table("usage_logs")
    op.drop_table("downloads")
    op.drop_table("feedback")
    op.drop_table("seos")
    op.drop_table("images")
    op.drop_table("audios")
    op.drop_index("ix_video_user_created", table_name="videos")
    op.drop_table("videos")
    op.drop_table("payments")
    op.drop_table("subscriptions")
    op.drop_table("users")
    op.drop_table("plans")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS paymentstatus")
    op.execute("DROP TYPE IF EXISTS paymentstatusenum")
    op.execute("DROP TYPE IF EXISTS feedbackcategory")
