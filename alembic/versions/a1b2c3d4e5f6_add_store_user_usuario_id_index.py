"""add store_user usuario_id index

Revision ID: a1b2c3d4e5f6
Revises: 7a8b9c0d1e2f
Create Date: 2026-06-16

"""
from typing import Sequence, Union

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "7a8b9c0d1e2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_tienda_usuario_usuario_id", "tienda_usuario", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_tienda_usuario_usuario_id", table_name="tienda_usuario")
