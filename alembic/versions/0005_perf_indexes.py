"""Performance indexes: soft-delete filters, composite event/camera patterns

Revision ID: 0005_perf_indexes
Revises: 0004_indexes_and_cleanup
Create Date: 2026-06-28
"""
from alembic import op

revision = "0005_perf_indexes"
down_revision = "0004_indexes_and_cleanup"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # evento: every list query filters eliminado=false then orders by created_at
    op.create_index("ix_evento_eliminado", "evento", ["eliminado"])
    op.create_index("ix_evento_eliminado_created", "evento", ["eliminado", "created_at"])

    # camara: same pattern for camera listings
    op.create_index("ix_camara_eliminado", "camara", ["eliminado"])
    op.create_index("ix_camara_eliminado_tienda", "camara", ["eliminado", "tienda_id"])

    # alerta: unread-count query (estado != descartada AND leida = false)
    op.create_index("ix_alerta_estado_leida", "alerta", ["estado", "leida"])


def downgrade() -> None:
    op.drop_index("ix_alerta_estado_leida", table_name="alerta")
    op.drop_index("ix_camara_eliminado_tienda", table_name="camara")
    op.drop_index("ix_camara_eliminado", table_name="camara")
    op.drop_index("ix_evento_eliminado_created", table_name="evento")
    op.drop_index("ix_evento_eliminado", table_name="evento")
