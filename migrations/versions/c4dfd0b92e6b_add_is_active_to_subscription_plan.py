"""add_is_active_to_subscription_plan

Revision ID: c4dfd0b92e6b
Revises: 7da6e3c7cab0
Create Date: 2026-06-27 02:24:18.387610

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c4dfd0b92e6b'
down_revision: str | None = '7da6e3c7cab0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('planes_suscripcion', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text("true")))


def downgrade() -> None:
    op.drop_column('planes_suscripcion', 'is_active')
