"""add version column

Revision ID: add_version_column
Revises: add_preferencias_enum
Create Date: 2026-06-11 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'add_version_column'
down_revision: str | None = 'add_preferencias_enum'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica la migración agregando la columna version."""
    # Agregar columna 'version' a empresas, roles, activos, ubicaciones
    for table in ["empresas", "roles", "activos", "ubicaciones"]:
        op.add_column(table, sa.Column("version", sa.Integer(), nullable=False, server_default="1"))


def downgrade() -> None:
    """Revierte la migración eliminando la columna version."""
    for table in ["empresas", "roles", "activos", "ubicaciones"]:
        op.drop_column(table, "version")
