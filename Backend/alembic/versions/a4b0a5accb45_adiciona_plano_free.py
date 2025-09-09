"""adiciona plano free"""

from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.sql import table, column
from sqlalchemy import String, Float, Boolean, Integer, Uuid

# Revisão
revision = 'a4b0a5accb45'
down_revision = 'full_schema_0001'
branch_labels = None
depends_on = None

def upgrade():
    plans_table = table(
        "plans",
        column("id", Uuid),
        column("name", String),
        column("description", String),
        column("price", Float),
        column("is_active", Boolean),
        column("max_video_duration", Integer),
    )

    op.bulk_insert(plans_table, [
        {
            "id": uuid.uuid4(),  # ✅ ID gerado corretamente como UUID
            "name": "free",
            "description": "Plano gratuito com visualização apenas.",
            "price": 0.0,
            "is_active": True,
            "max_video_duration": 0,
        },
    ])
