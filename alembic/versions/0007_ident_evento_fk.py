"""Add evento_id FK and make evento_imagen_id nullable in identificacion

Revision ID: 0007_ident_evento_fk
Revises: 0006_ident_fields
Create Date: 2026-06-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_ident_evento_fk"
down_revision = "0006_ident_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "identificacion",
        "evento_imagen_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.add_column(
        "identificacion",
        sa.Column("evento_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_identificacion_evento_id",
        "identificacion", "evento",
        ["evento_id"], ["id"],
    )
    op.create_index("ix_identificacion_evento_id", "identificacion", ["evento_id"])


def downgrade() -> None:
    op.drop_index("ix_identificacion_evento_id", table_name="identificacion")
    op.drop_constraint("fk_identificacion_evento_id", "identificacion", type_="foreignkey")
    op.drop_column("identificacion", "evento_id")
    op.alter_column(
        "identificacion",
        "evento_imagen_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
