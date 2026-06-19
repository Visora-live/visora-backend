"""initial schema v20b

Revision ID: 0001_initial_schema_v20b
Revises:
Create Date: 2026-06-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema_v20b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rol",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tipo"),
    )

    op.create_table(
        "tienda",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("direccion", sa.String(200), nullable=True),
        sa.Column("ruc", sa.String(20), nullable=True),
        sa.Column("estado_tienda", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("licencia_inicio", sa.Date(), nullable=True),
        sa.Column("licencia_fin", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ruc"),
    )
    op.create_index("ix_tienda_estado_tienda", "tienda", ["estado_tienda"])

    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("estado_acceso", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("contrasena", sa.String(255), nullable=False),
        sa.Column("rol_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["rol_id"], ["rol.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_usuario_rol_id", "usuario", ["rol_id"])

    op.create_table(
        "camara",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre_cam", sa.String(100), nullable=False),
        sa.Column("direccion_ip", sa.String(255), nullable=False),
        sa.Column("puerto", sa.Integer(), nullable=False, server_default="8080"),
        sa.Column("ubicacion_camara", sa.String(200), nullable=True),
        sa.Column("estado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "source_type", sa.String(30), nullable=False, server_default=sa.text("'rtsp_h264'")
        ),
        sa.Column("protocolo", sa.String(10), nullable=False, server_default=sa.text("'rtsp'")),
        sa.Column("tienda_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["tienda_id"], ["tienda.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_camara_tienda_id", "camara", ["tienda_id"])
    op.create_index("ix_camara_estado", "camara", ["estado"])

    op.create_table(
        "tienda_usuario",
        sa.Column("tienda_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["tienda_id"], ["tienda.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"]),
        sa.PrimaryKeyConstraint("tienda_id", "usuario_id"),
    )
    op.create_index("ix_tienda_usuario_usuario_id", "tienda_usuario", ["usuario_id"])

    op.create_table(
        "evento",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default=sa.text("'abierto'")),
        sa.Column(
            "fecha_hora",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("camara_id", sa.Integer(), nullable=False),
        sa.Column(
            "tipo", sa.String(30), nullable=False, server_default=sa.text("'desconocido'")
        ),
        sa.Column(
            "severidad", sa.String(20), nullable=False, server_default=sa.text("'media'")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["camara_id"], ["camara.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evento_camara_id", "evento", ["camara_id"])
    op.create_index("ix_evento_estado", "evento", ["estado"])
    op.create_index("ix_evento_fecha_hora", "evento", ["fecha_hora"])

    op.create_table(
        "evento_imagen",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("storage_ref", sa.Text(), nullable=False),
        sa.Column("evento_id", sa.Integer(), nullable=False),
        sa.Column(
            "es_frame_representativo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("confianza_arma", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("confianza_rostro", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "storage_provider", sa.String(20), nullable=False, server_default=sa.text("'local'")
        ),
        sa.Column("filename", sa.String(255), nullable=True),
        sa.Column("content_type", sa.String(50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evento_imagen_evento_id", "evento_imagen", ["evento_id"])

    op.create_table(
        "identificacion",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evento_imagen_id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=True),
        sa.Column("apellido", sa.String(100), nullable=True),
        sa.Column("dni", sa.String(20), nullable=True),
        sa.Column(
            "confianza_identificacion", sa.Float(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column("fuente", sa.String(50), nullable=False, server_default=sa.text("'manual'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["evento_imagen_id"], ["evento_imagen.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_identificacion_evento_imagen_id", "identificacion", ["evento_imagen_id"])
    op.create_index("ix_identificacion_dni", "identificacion", ["dni"])

    op.create_table(
        "alerta",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("tipo", sa.String(40), nullable=False, server_default=sa.text("'manual'")),
        sa.Column(
            "severidad", sa.String(20), nullable=False, server_default=sa.text("'media'")
        ),
        sa.Column(
            "estado", sa.String(20), nullable=False, server_default=sa.text("'abierta'")
        ),
        sa.Column("leida", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("evento_id", sa.Integer(), nullable=True),
        sa.Column("camara_id", sa.Integer(), nullable=True),
        sa.Column("tienda_id", sa.Integer(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["camara_id"], ["camara.id"]),
        sa.ForeignKeyConstraint(["evento_id"], ["evento.id"]),
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
    op.drop_table("alerta")
    op.drop_table("identificacion")
    op.drop_table("evento_imagen")
    op.drop_table("evento")
    op.drop_table("tienda_usuario")
    op.drop_table("camara")
    op.drop_table("usuario")
    op.drop_table("tienda")
    op.drop_table("rol")
