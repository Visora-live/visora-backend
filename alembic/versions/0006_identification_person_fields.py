"""Add apellido_materno and edad to identificacion

Revision ID: 0006_ident_fields
Revises: 0005_perf_indexes
Create Date: 2026-06-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_ident_fields"
down_revision = "0005_perf_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "identificacion",
        sa.Column("apellido_materno", sa.String(100), nullable=True),
    )
    op.add_column(
        "identificacion",
        sa.Column("edad", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("identificacion", "edad")
    op.drop_column("identificacion", "apellido_materno")
