"""add solicitud_recuperacion table

Revision ID: 0002_recovery_requests
Revises: 0001_initial_schema_v20b
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_recovery_requests"
down_revision = "0001_initial_schema_v20b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "solicitud_recuperacion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("identificador", sa.String(150), nullable=False),
        sa.Column("celular", sa.String(30), nullable=True),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("leida", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("solicitud_recuperacion")
