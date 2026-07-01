"""crear_tabla_entradas_inventario

Revision ID: 6053b37250c9
Revises: 77d0cc644c40
Create Date: 2026-06-30 22:23:13.291168

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6053b37250c9'
down_revision: str | None = '77d0cc644c40'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "entradas_inventario",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("repuesto_id", sa.Uuid(), nullable=False),
        sa.Column("ordenes_trabajo_id", sa.Uuid(), nullable=True),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("tipo_movimiento", sa.String(length=50), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("moneda", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("fecha_movimiento", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repuesto_id"], ["inventario_repuestos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ordenes_trabajo_id"], ["ordenes_trabajo.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_entradas_inventario_empresa_id", "entradas_inventario", ["empresa_id"])
    op.create_index("ix_entradas_inventario_empresa_repuesto", "entradas_inventario", ["empresa_id", "repuesto_id"])
    op.create_index("ix_entradas_inventario_empresa_ot", "entradas_inventario", ["empresa_id", "ordenes_trabajo_id"])


def downgrade() -> None:
    op.drop_table("entradas_inventario")
