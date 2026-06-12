"""create base tables

Revision ID: 3f2a1b4c5d6e
Revises:
Create Date: 2026-06-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "3f2a1b4c5d6e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rol",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(50), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )

    op.create_table(
        "tienda",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("direccion", sa.String(200), nullable=True),
        sa.Column("ruc", sa.String(20), nullable=True),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'activa'")),
        sa.Column("licencia_inicio", sa.Date(), nullable=True),
        sa.Column("licencia_fin", sa.Date(), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ruc"),
    )
    op.create_index("ix_tienda_estado", "tienda", ["estado"])

    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'activo'")),
        sa.Column("rol_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["rol_id"], ["rol.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_usuario_rol_id", "usuario", ["rol_id"])

    op.create_table(
        "camara",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("host", sa.String(100), nullable=False),
        sa.Column("puerto", sa.Integer(), nullable=False, server_default=sa.text("8080")),
        sa.Column("ubicacion", sa.String(200), nullable=True),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'offline'")),
        sa.Column(
            "source_type", sa.String(30), nullable=False, server_default=sa.text("'rtsp_h264'")
        ),
        sa.Column(
            "protocolo", sa.String(10), nullable=False, server_default=sa.text("'rtsp'")
        ),
        sa.Column("tienda_id", sa.Integer(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_camara_tienda_id", "camara", ["tienda_id"])
    op.create_index("ix_camara_estado", "camara", ["estado"])


def downgrade() -> None:
    op.drop_index("ix_camara_estado", table_name="camara")
    op.drop_index("ix_camara_tienda_id", table_name="camara")
    op.drop_table("camara")

    op.drop_index("ix_usuario_rol_id", table_name="usuario")
    op.drop_table("usuario")

    op.drop_index("ix_tienda_estado", table_name="tienda")
    op.drop_table("tienda")

    op.drop_table("rol")
