"""Add composite indexes for common query patterns; drop dead celular column

Revision ID: 0004_indexes_and_cleanup
Revises: 0003_soft_delete_flags
Create Date: 2026-06-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_indexes_and_cleanup"
down_revision = "0003_soft_delete_flags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── evento ────────────────────────────────────────────────────────────────
    # Common list query: filter by tienda_id (via store join) + tipo + estado
    op.create_index("ix_evento_camara_tipo", "evento", ["camara_id", "tipo"])
    op.create_index("ix_evento_camara_estado", "evento", ["camara_id", "estado"])
    op.create_index("ix_evento_severidad", "evento", ["severidad"])

    # ── alerta ────────────────────────────────────────────────────────────────
    # Common list query: filter by tienda_id + estado + severidad
    op.create_index("ix_alerta_tienda_estado", "alerta", ["tienda_id", "estado"])
    op.create_index("ix_alerta_tienda_tipo", "alerta", ["tienda_id", "tipo"])
    op.create_index("ix_alerta_tienda_severidad", "alerta", ["tienda_id", "severidad"])
    op.create_index("ix_alerta_leida", "alerta", ["leida"])

    # ── tienda_usuario ────────────────────────────────────────────────────────
    op.create_index("ix_tienda_usuario_tienda", "tienda_usuario", ["tienda_id"])

    # ── Drop dead column ──────────────────────────────────────────────────────
    op.drop_column("solicitud_recuperacion", "celular")


def downgrade() -> None:
    op.add_column(
        "solicitud_recuperacion",
        sa.Column("celular", sa.String(20), nullable=True),
    )
    op.drop_index("ix_tienda_usuario_tienda", table_name="tienda_usuario")
    op.drop_index("ix_alerta_leida", table_name="alerta")
    op.drop_index("ix_alerta_tienda_severidad", table_name="alerta")
    op.drop_index("ix_alerta_tienda_tipo", table_name="alerta")
    op.drop_index("ix_alerta_tienda_estado", table_name="alerta")
    op.drop_index("ix_evento_severidad", table_name="evento")
    op.drop_index("ix_evento_camara_estado", table_name="evento")
    op.drop_index("ix_evento_camara_tipo", table_name="evento")
