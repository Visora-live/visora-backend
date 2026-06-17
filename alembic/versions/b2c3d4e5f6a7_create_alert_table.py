"""create alert table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "alerta",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column(
            "tipo",
            sa.String(40),
            nullable=False,
            server_default=sa.text("'manual'"),
        ),
        sa.Column(
            "severidad",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'media'"),
        ),
        sa.Column(
            "estado",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'abierta'"),
        ),
        sa.Column("evento_id", sa.Integer(), nullable=True),
        sa.Column("camara_id", sa.Integer(), nullable=True),
        sa.Column("tienda_id", sa.Integer(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.ForeignKeyConstraint(["camara_id"], ["camara.id"]),
        sa.ForeignKeyConstraint(["tienda_id"], ["tienda.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerta_estado", "alerta", ["estado"])
    op.create_index("ix_alerta_severidad", "alerta", ["severidad"])
    op.create_index("ix_alerta_tipo", "alerta", ["tipo"])
    op.create_index("ix_alerta_evento_id", "alerta", ["evento_id"])
    op.create_index("ix_alerta_camara_id", "alerta", ["camara_id"])
    op.create_index("ix_alerta_tienda_id", "alerta", ["tienda_id"])
    op.create_index("ix_alerta_created_at", "alerta", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_alerta_created_at", table_name="alerta")
    op.drop_index("ix_alerta_tienda_id", table_name="alerta")
    op.drop_index("ix_alerta_camara_id", table_name="alerta")
    op.drop_index("ix_alerta_evento_id", table_name="alerta")
    op.drop_index("ix_alerta_tipo", table_name="alerta")
    op.drop_index("ix_alerta_severidad", table_name="alerta")
    op.drop_index("ix_alerta_estado", table_name="alerta")
    op.drop_table("alerta")
