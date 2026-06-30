"""add eliminado soft-delete flags to camara and evento

Revision ID: 0003_soft_delete_flags
Revises: 0002_recovery_requests
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_soft_delete_flags"
down_revision = "0002_recovery_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "camara",
        sa.Column("eliminado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "evento",
        sa.Column("eliminado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("evento", "eliminado")
    op.drop_column("camara", "eliminado")
