"""fix_system_audits_table

Corrige la tabla de auditorías del sistema:
- Renombra `system_audits` → `auditorias_sistema` (convención DBML española del proyecto)
- Agrega la columna `ocurrido_en` faltante (referenciada por el modelo ORM y el repositorio)
- Migra índices para reflejar el nuevo nombre de tabla

Revision ID: a1f3c9d82e45
Revises: 823874b35563
Create Date: 2026-06-27 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1f3c9d82e45"
down_revision: str | None = "823874b35563"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Eliminar índices existentes con el nombre de la tabla vieja
    op.drop_index("ix_system_audits_usuario_id", table_name="system_audits")
    op.drop_index("ix_system_audits_id", table_name="system_audits")
    op.drop_index("ix_system_audits_empresa_id", table_name="system_audits")

    # 2. Renombrar la tabla al nombre correcto en español
    op.rename_table("system_audits", "auditorias_sistema")

    # 3. Agregar la columna `ocurrido_en` faltante
    #    Se inicializa con now() para cumplir NOT NULL en filas existentes
    op.add_column(
        "auditorias_sistema",
        sa.Column(
            "ocurrido_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    # Quitar el server_default una vez aplicado (valor por defecto es responsabilidad del dominio)
    op.alter_column("auditorias_sistema", "ocurrido_en", server_default=None)

    # 4. Cambiar columna `detalles` de JSON genérico a JSONB (optimizado para PostgreSQL)
    op.alter_column(
        "auditorias_sistema",
        "detalles",
        type_=postgresql.JSONB(),
        existing_type=sa.JSON(),
        existing_nullable=False,
    )

    # 5. Recrear índices con el nuevo nombre de tabla
    op.create_index(
        "ix_auditorias_sistema_empresa_id",
        "auditorias_sistema",
        ["empresa_id"],
        unique=False,
    )
    op.create_index(
        "ix_auditorias_sistema_id",
        "auditorias_sistema",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_auditorias_sistema_usuario_id",
        "auditorias_sistema",
        ["usuario_id"],
        unique=False,
    )


def downgrade() -> None:
    # 1. Eliminar índices del nombre nuevo
    op.drop_index("ix_auditorias_sistema_usuario_id", table_name="auditorias_sistema")
    op.drop_index("ix_auditorias_sistema_id", table_name="auditorias_sistema")
    op.drop_index("ix_auditorias_sistema_empresa_id", table_name="auditorias_sistema")

    # 2. Revertir columna detalles de JSONB a JSON
    op.alter_column(
        "auditorias_sistema",
        "detalles",
        type_=sa.JSON(),
        existing_type=postgresql.JSONB(),
        existing_nullable=False,
    )

    # 3. Eliminar la columna ocurrido_en agregada
    op.drop_column("auditorias_sistema", "ocurrido_en")

    # 4. Renombrar de vuelta a nombre original
    op.rename_table("auditorias_sistema", "system_audits")

    # 5. Recrear los índices originales
    op.create_index("ix_system_audits_usuario_id", "system_audits", ["usuario_id"], unique=False)
    op.create_index("ix_system_audits_id", "system_audits", ["id"], unique=False)
    op.create_index(
        "ix_system_audits_empresa_id", "system_audits", ["empresa_id"], unique=False
    )
