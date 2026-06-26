"""create_work_orders_tables

Crea las 3 tablas del módulo ordenes_trabajo:
- ordenes_trabajo
- tecnicos_ordenes_trabajo
- logs_estados_ordenes_trabajo

Revision ID: 94511a515fbe
Revises: f1a2b3c4d5e6
Create Date: 2026-06-26 19:54:18.261900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "94511a515fbe"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- ordenes_trabajo ---
    op.create_table(
        "ordenes_trabajo",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("codigo_ot", sa.String(length=30), nullable=False),
        sa.Column("activo_id", sa.Uuid(), nullable=False),
        sa.Column("reporte_id", sa.Uuid(), nullable=True),
        sa.Column("plan_id", sa.Uuid(), nullable=True),
        sa.Column("supervisor_id", sa.Uuid(), nullable=True),
        sa.Column(
            "tipo",
            sa.Enum("preventivo", "correctivo", "predictivo", name="maintenancetype"),
            nullable=False,
        ),
        sa.Column(
            "estado",
            sa.Enum(
                "abierta", "en_proceso", "pausada", "cerrada", "cancelada",
                name="workorderstatus",
            ),
            nullable=False,
        ),
        sa.Column("fecha_apertura", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "fecha_inicio_trabajo", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("fecha_cierre", sa.DateTime(timezone=True), nullable=True),
        sa.Column("descripcion_trabajo", sa.Text(), nullable=True),
        sa.Column(
            "costo_estimado", sa.Numeric(precision=12, scale=2), nullable=True
        ),
        sa.Column("costo_real", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("moneda", sa.String(length=3), nullable=False),
        sa.Column("validado_por_id", sa.Uuid(), nullable=True),
        sa.Column("fecha_validacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["activo_id"], ["activos.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["empresa_id"], ["empresas.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["supervisor_id"], ["usuarios.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["validado_por_id"], ["usuarios.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "empresa_id", "codigo_ot", name="uq_ordenes_trabajo_empresa_codigo_ot"
        ),
    )
    op.create_index(
        op.f("ix_ordenes_trabajo_empresa_id"),
        "ordenes_trabajo",
        ["empresa_id"],
        unique=False,
    )

    # --- logs_estados_ordenes_trabajo ---
    op.create_table(
        "logs_estados_ordenes_trabajo",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("ordenes_trabajo_id", sa.Uuid(), nullable=False),
        sa.Column(
            "estado_anterior",
            sa.Enum(
                "abierta", "en_proceso", "pausada", "cerrada", "cancelada",
                name="workorderstatus",
            ),
            nullable=True,
        ),
        sa.Column(
            "estado_nuevo",
            sa.Enum(
                "abierta", "en_proceso", "pausada", "cerrada", "cancelada",
                name="workorderstatus",
            ),
            nullable=False,
        ),
        sa.Column("cambiado_por_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cambiado_por_id"], ["usuarios.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["empresa_id"], ["empresas.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["ordenes_trabajo_id"],
            ["ordenes_trabajo.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_logs_estados_ordenes_trabajo_empresa_id"),
        "logs_estados_ordenes_trabajo",
        ["empresa_id"],
        unique=False,
    )

    # --- tecnicos_ordenes_trabajo ---
    op.create_table(
        "tecnicos_ordenes_trabajo",
        sa.Column("ordenes_trabajo_id", sa.Uuid(), nullable=False),
        sa.Column("tecnico_id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["empresa_id"], ["empresas.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["ordenes_trabajo_id"],
            ["ordenes_trabajo.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tecnico_id"], ["usuarios.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("ordenes_trabajo_id", "tecnico_id"),
    )
    op.create_index(
        op.f("ix_tecnicos_ordenes_trabajo_empresa_id"),
        "tecnicos_ordenes_trabajo",
        ["empresa_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_tecnicos_ordenes_trabajo_empresa_id"),
        table_name="tecnicos_ordenes_trabajo",
    )
    op.drop_table("tecnicos_ordenes_trabajo")
    op.drop_index(
        op.f("ix_logs_estados_ordenes_trabajo_empresa_id"),
        table_name="logs_estados_ordenes_trabajo",
    )
    op.drop_table("logs_estados_ordenes_trabajo")
    op.drop_index(
        op.f("ix_ordenes_trabajo_empresa_id"),
        table_name="ordenes_trabajo",
    )
    op.drop_table("ordenes_trabajo")
