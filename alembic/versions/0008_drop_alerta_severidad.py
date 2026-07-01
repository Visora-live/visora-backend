"""Drop unused alerta.severidad column (never read after evento.severidad covers it)

Revision ID: 0008_drop_alerta_severidad
Revises: 0007_ident_evento_fk
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_drop_alerta_severidad"
down_revision = "0007_ident_evento_fk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Both indexes reference severidad (0001 single-column, 0004 composite) — drop
    # them first or the DROP COLUMN fails.
    op.drop_index("ix_alerta_tienda_severidad", table_name="alerta")
    op.drop_index("ix_alerta_severidad", table_name="alerta")
    op.drop_column("alerta", "severidad")


def downgrade() -> None:
    op.add_column(
        "alerta",
        sa.Column("severidad", sa.String(20), nullable=False, server_default=sa.text("'media'")),
    )
    op.create_index("ix_alerta_severidad", "alerta", ["severidad"])
    op.create_index("ix_alerta_tienda_severidad", "alerta", ["tienda_id", "severidad"])
