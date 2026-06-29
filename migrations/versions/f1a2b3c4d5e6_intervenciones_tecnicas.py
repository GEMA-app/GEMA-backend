"""intervenciones_tecnicas

Revision ID: f1a2b3c4d5e6
Revises: 10468db73cf1
Create Date: 2026-06-26 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: str | None = "e4a7b4eca0ab"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "intervenciones_tecnicas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("ordenes_trabajo_id", sa.Uuid(), nullable=False),
        sa.Column("tecnico_id", sa.Uuid(), nullable=False),
        sa.Column("tareas_realizadas", sa.Text(), nullable=False),
        sa.Column("fecha_inicio", sa.DateTime(), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(), nullable=True),
        sa.Column("horas_hombre", sa.Numeric(5, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        # FK a ordenes_trabajo se agregará cuando exista la tabla
        # sa.ForeignKeyConstraint(
        #     ["ordenes_trabajo_id"],
        #     ["ordenes_trabajo.id"],
        #     ondelete="CASCADE",
        # ),
        sa.ForeignKeyConstraint(
            ["tecnico_id"],
            ["usuarios.id"],
        ),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresas.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_intervenciones_tecnicas_empresa_id"),
        "intervenciones_tecnicas",
        ["empresa_id"],
    )
    op.create_index(
        op.f("ix_intervenciones_tecnicas_ordenes_trabajo_id"),
        "intervenciones_tecnicas",
        ["ordenes_trabajo_id"],
    )
    op.create_index(
        op.f("ix_intervenciones_tecnicas_tecnico_id"),
        "intervenciones_tecnicas",
        ["tecnico_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_intervenciones_tecnicas_tecnico_id"),
        table_name="intervenciones_tecnicas",
    )
    op.drop_index(
        op.f("ix_intervenciones_tecnicas_ordenes_trabajo_id"),
        table_name="intervenciones_tecnicas",
    )
    op.drop_index(
        op.f("ix_intervenciones_tecnicas_empresa_id"),
        table_name="intervenciones_tecnicas",
    )
    op.drop_table("intervenciones_tecnicas")
