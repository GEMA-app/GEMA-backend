"""Agrega valor 'preferencias' al enum permissionmodule de PostgreSQL.

El enum permissionmodule se creó originalmente con 5 valores:
activos, mantenimiento, inventario, reportes, administracion

Pero el código Python (PermissionModule enum) tiene 6:
incluye 'preferencias' para el módulo de preferencias de usuario.

Esta migración agrega el valor faltante sin necesidad de recrear el tipo.
"""

from typing import Sequence, Union
from alembic import op

revision: str = "add_preferencias_enum"
down_revision: Union[str, None] = "abc123_case_insensitive_asset"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE permissionmodule ADD VALUE 'preferencias'")


def downgrade() -> None:
    # PostgreSQL no permite eliminar valores de un enum directamente.
    # Para hacer downgrade habría que recrear el tipo completo.
    # Se documenta como limitación conocida.
    pass
