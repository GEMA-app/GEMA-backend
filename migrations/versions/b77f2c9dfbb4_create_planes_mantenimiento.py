"""create_planes_mantenimiento

Crea la tabla ``planes_mantenimiento`` para el módulo MaintenancePlan.

Revision ID: b77f2c9dfbb4
Revises: 38790d306557
Create Date: 2026-06-27 19:09:15.191250

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b77f2c9dfbb4'
down_revision: str | None = '38790d306557'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('planes_mantenimiento',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('activo_id', sa.Uuid(), nullable=False),
    sa.Column('tecnico_responsable_id', sa.Uuid(), nullable=True),
    sa.Column('nombre', sa.String(length=255), nullable=False),
    sa.Column('tipo', sa.Enum('preventivo', 'correctivo', 'predictivo', name='maintenancetype'), nullable=False),
    sa.Column('intervalo_dias', sa.Integer(), nullable=False),
    sa.Column('proxima_ejecucion', sa.Date(), nullable=False),
    sa.Column('descripcion_tareas', sa.Text(), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('empresa_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['activo_id'], ['activos.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tecnico_responsable_id'], ['usuarios.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_planes_mantenimiento_empresa_activo', 'planes_mantenimiento', ['empresa_id', 'activo_id'], unique=False)
    op.create_index('ix_planes_mantenimiento_empresa_id', 'planes_mantenimiento', ['empresa_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_planes_mantenimiento_empresa_id', table_name='planes_mantenimiento')
    op.drop_index('ix_planes_mantenimiento_empresa_activo', table_name='planes_mantenimiento')
    op.drop_table('planes_mantenimiento')
    op.execute("DROP TYPE IF EXISTS maintenancetype")
