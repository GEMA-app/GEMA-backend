"""add_version_to_work_order

Revision ID: 77d0cc644c40
Revises: 7ee9f62274a0
Create Date: 2026-06-29 08:48:40.335255

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77d0cc644c40'
down_revision: str | None = '7ee9f62274a0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('ordenes_trabajo', sa.Column('version', sa.Integer(), nullable=True))
    op.execute("UPDATE ordenes_trabajo SET version = 1 WHERE version IS NULL")
    op.alter_column('ordenes_trabajo', 'version', nullable=False)


def downgrade() -> None:
    op.drop_column('ordenes_trabajo', 'version')
