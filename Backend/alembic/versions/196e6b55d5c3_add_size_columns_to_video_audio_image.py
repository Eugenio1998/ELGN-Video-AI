"""add size columns to video, audio, image"""

from alembic import op
import sqlalchemy as sa


# Revisão e dependência
revision = '196e6b55d5c3'
down_revision = 'a4b0a5accb45'
branch_labels = None
depends_on = None


def upgrade():
    # 📹 Vídeos
    op.add_column("videos", sa.Column("size", sa.Integer(), nullable=True))
    op.add_column("videos", sa.Column("status", sa.String(), nullable=True))

    # 🎵 Áudios
    op.add_column("audios", sa.Column("size", sa.Integer(), nullable=True))

    # 🖼️ Imagens
    op.add_column("images", sa.Column("size", sa.Integer(), nullable=True))


def downgrade():
    # Reversão
    op.drop_column("images", "size")
    op.drop_column("audios", "size")
    op.drop_column("videos", "status")
    op.drop_column("videos", "size")
