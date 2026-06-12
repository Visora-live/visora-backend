"""create operational tables

Revision ID: 7a8b9c0d1e2f
Revises: 3f2a1b4c5d6e
Create Date: 2026-06-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "7a8b9c0d1e2f"
down_revision: Union[str, None] = "3f2a1b4c5d6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tienda_usuario",
        sa.Column("tienda_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'activo'")),
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
        sa.ForeignKeyConstraint(["tienda_id"], ["tienda.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("tienda_id", "usuario_id"),
    )

    op.create_table(
        "evento",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False, server_default=sa.text("'desconocido'")),
        sa.Column("severidad", sa.String(20), nullable=False, server_default=sa.text("'media'")),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'abierto'")),
        sa.Column(
            "fecha_hora",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("camara_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["camara_id"], ["camara.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evento_camara_id", "evento", ["camara_id"])
    op.create_index("ix_evento_estado", "evento", ["estado"])
    op.create_index("ix_evento_severidad", "evento", ["severidad"])
    op.create_index("ix_evento_fecha_hora", "evento", ["fecha_hora"])

    op.create_table(
        "evidencia",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False, server_default=sa.text("'snapshot'")),
        sa.Column(
            "storage_provider",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'local'"),
        ),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("storage_bucket", sa.String(200), nullable=True),
        sa.Column("filename", sa.String(255), nullable=True),
        sa.Column("content_type", sa.String(50), nullable=True),
        sa.Column(
            "ai_processed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evidencia_evento_id", "evidencia", ["evento_id"])

    op.create_table(
        "identificacion",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("evidencia_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=True),
        sa.Column("apellido", sa.String(100), nullable=True),
        sa.Column("dni", sa.String(20), nullable=True),
        sa.Column("confianza", sa.Float(), nullable=True),
        sa.Column("fuente", sa.String(50), nullable=False, server_default=sa.text("'manual'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["evidencia_id"], ["evidencia.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_identificacion_evidencia_id", "identificacion", ["evidencia_id"])
    op.create_index("ix_identificacion_dni", "identificacion", ["dni"])


def downgrade() -> None:
    op.drop_index("ix_identificacion_dni", table_name="identificacion")
    op.drop_index("ix_identificacion_evidencia_id", table_name="identificacion")
    op.drop_table("identificacion")

    op.drop_index("ix_evidencia_evento_id", table_name="evidencia")
    op.drop_table("evidencia")

    op.drop_index("ix_evento_fecha_hora", table_name="evento")
    op.drop_index("ix_evento_severidad", table_name="evento")
    op.drop_index("ix_evento_estado", table_name="evento")
    op.drop_index("ix_evento_camara_id", table_name="evento")
    op.drop_table("evento")

    op.drop_table("tienda_usuario")
