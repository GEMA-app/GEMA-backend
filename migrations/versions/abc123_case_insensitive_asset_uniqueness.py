"""Agrega índices únicos funcionales case-insensitive para activos.

ORDEN CORREGIDO v9.1:
1. DROP constraints viejos (case-sensitive)
2. Normalizar datos existentes a lowercase
3. CREATE índices funcionales (case-insensitive)

El orden original (Normalizar → DROP → CREATE) fallaba si existían
registros como "ABC-123" y "abc-123" porque UPDATE LOWER colisionaba
con el UniqueConstraint aún activo.
"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy import text

revision: str = "abc123_case_insensitive_asset"
down_revision: Union[str, None] = "514893182b42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Paso 1: Diagnosticar duplicados potenciales (no blocking, solo report)
    conn = op.get_bind()
    result = conn.execute(
        text(
            "SELECT LOWER(codigo_activo) AS codigo_activo, COUNT(*) AS count "
            "FROM activos "
            "GROUP BY empresa_id, LOWER(codigo_activo) "
            "HAVING COUNT(*) > 1"
        )
    )
    duplicates = result.fetchall()
    if duplicates:
        import warnings
        warnings.warn(
            f"Se detectaron {len(duplicates)} grupos de activos con "
            f"códigos duplicados case-insensitive. Revisar antes de migrar."
        )

    # Paso 2: DROP constraints viejos (primero, para permitir UPDATE LOWER)
    op.drop_constraint(
        "uq_activos_empresa_codigo_activo", "activos", type_="unique"
    )
    op.drop_constraint(
        "uq_activos_empresa_serial_interno", "activos", type_="unique"
    )

    # Paso 3: Normalizar datos existentes a lowercase (ya sin constraint)
    op.execute(
        "UPDATE activos SET codigo_activo = LOWER(codigo_activo)"
        " WHERE codigo_activo != LOWER(codigo_activo)"
    )
    op.execute(
        "UPDATE activos SET serial_interno = LOWER(serial_interno)"
        " WHERE serial_interno != LOWER(serial_interno)"
    )

    # Paso 4: CREATE índices funcionales
    op.execute(
        "CREATE UNIQUE INDEX uq_activos_empresa_codigo_activo_lower"
        " ON activos (empresa_id, LOWER(codigo_activo))"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_activos_empresa_serial_interno_lower"
        " ON activos (empresa_id, LOWER(serial_interno))"
    )


def downgrade() -> None:
    # Restaurar constraints originales
    op.create_unique_constraint(
        "uq_activos_empresa_codigo_activo", "activos",
        ["empresa_id", "codigo_activo"]
    )
    op.create_unique_constraint(
        "uq_activos_empresa_serial_interno", "activos",
        ["empresa_id", "serial_interno"]
    )
    op.drop_index("uq_activos_empresa_codigo_activo_lower", table_name="activos")
    op.drop_index("uq_activos_empresa_serial_interno_lower", table_name="activos")
