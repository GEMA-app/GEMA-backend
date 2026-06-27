"""rename_hashed_password_to_password_hash

Renombra la columna hashed_password → password_hash en la tabla usuarios
para alinearla con el DBML y el nombre del atributo de dominio.

Revision ID: 38790d306557
Revises: 7da6e3c7cab0
Create Date: 2026-06-27 08:03:51.749320

"""
from typing import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '38790d306557'
down_revision: str | None = '7da6e3c7cab0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column('usuarios', 'hashed_password', new_column_name='password_hash')


def downgrade() -> None:
    op.alter_column('usuarios', 'password_hash', new_column_name='hashed_password')
