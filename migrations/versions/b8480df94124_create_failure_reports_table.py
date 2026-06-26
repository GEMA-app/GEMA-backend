"""create_failure_reports_table

Revision ID: b8480df94124
Revises: 7da6e3c7cab0
Create Date: 2026-06-26 12:00:00.000000

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8480df94124'
down_revision: str | None = '7da6e3c7cab0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('failure_reports',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('priority',
            sa.Enum('critica', 'alta', 'media', 'baja',
                    name='prioritylevel'),
            nullable=False, server_default='media'),
        sa.Column('reported_by', sa.String(length=255), nullable=False),
        sa.Column('status',
            sa.Enum('pendiente', 'en_proceso', 'atendido', 'descartado',
                    name='reportstatus'),
            nullable=False, server_default='pendiente'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('empresa_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'],
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_failure_reports_empresa_id'),
                    'failure_reports', ['empresa_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_failure_reports_empresa_id'),
                  table_name='failure_reports')
    op.drop_table('failure_reports')
    op.execute('DROP TYPE IF EXISTS prioritylevel')
    op.execute('DROP TYPE IF EXISTS reportstatus')
