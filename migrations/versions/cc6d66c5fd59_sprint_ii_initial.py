"""sprint_ii_initial

Revision ID: cc6d66c5fd59
Revises: 
Create Date: 2026-06-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc6d66c5fd59'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear planes_suscripcion
    op.create_table('planes_suscripcion',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('max_activos', sa.Integer(), nullable=True),
        sa.Column('max_usuarios', sa.Integer(), nullable=True),
        sa.Column('precio_mensual_usd', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre')
    )

    # Crear empresas
    op.create_table('empresas',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('plan_id', sa.Uuid(), nullable=True),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=63), nullable=False),
        sa.Column('rif', sa.String(length=50), nullable=True),
        sa.Column('email_contacto', sa.String(length=255), nullable=True),
        sa.Column('estado', sa.Enum('activa', 'suspendida', 'cancelada', name='companystatus'), nullable=False),
        sa.Column('trial_hasta', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['planes_suscripcion.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_empresas_slug'), 'empresas', ['slug'], unique=True)

    # Crear usuarios
    op.create_table('usuarios',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('empresa_id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('telefono', sa.String(length=50), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('empresa_id', 'email', name='uq_usuarios_empresa_email')
    )
    op.create_index(op.f('ix_usuarios_empresa_id'), 'usuarios', ['empresa_id'], unique=False)

    # Crear roles
    op.create_table('roles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('empresa_id', sa.Uuid(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('empresa_id', 'nombre', name='uq_roles_empresa_nombre')
    )
    op.create_index(op.f('ix_roles_empresa_id'), 'roles', ['empresa_id'], unique=False)

    # Crear roles_usuarios
    op.create_table('roles_usuarios',
        sa.Column('usuario_id', sa.Uuid(), nullable=False),
        sa.Column('rol_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('usuario_id', 'rol_id')
    )

    # Crear permisos
    op.create_table('permisos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('empresa_id', sa.Uuid(), nullable=False),
        sa.Column('rol_id', sa.Uuid(), nullable=False),
        sa.Column('modulo', sa.Enum('activos', 'mantenimiento', 'inventario', 'reportes', 'administracion', name='permissionmodule'), nullable=False),
        sa.Column('puede_ver', sa.Boolean(), nullable=False),
        sa.Column('puede_crear', sa.Boolean(), nullable=False),
        sa.Column('puede_editar', sa.Boolean(), nullable=False),
        sa.Column('puede_eliminar', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('empresa_id', 'rol_id', 'modulo', name='uq_permisos_empresa_rol_modulo')
    )
    op.create_index(op.f('ix_permisos_empresa_id'), 'permisos', ['empresa_id'], unique=False)

    # Crear ubicaciones
    op.create_table('ubicaciones',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('empresa_id', sa.Uuid(), nullable=False),
        sa.Column('parent_id', sa.Uuid(), nullable=True),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('tipo', sa.Enum('sede', 'planta', 'area', 'seccion', name='locationtype'), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['ubicaciones.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ubicaciones_empresa_parent', 'ubicaciones', ['empresa_id', 'parent_id'], unique=False)
    op.create_index(op.f('ix_ubicaciones_empresa_id'), 'ubicaciones', ['empresa_id'], unique=False)

    # Crear categorias_articulos
    op.create_table('categorias_articulos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('empresa_id', sa.Uuid(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('empresa_id', 'nombre', name='uq_categorias_articulos_empresa_nombre')
    )
    op.create_index(op.f('ix_categorias_articulos_empresa_id'), 'categorias_articulos', ['empresa_id'], unique=False)

    # Crear articulos_catalogo
    op.create_table('articulos_catalogo',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('empresa_id', sa.Uuid(), nullable=False),
        sa.Column('categoria_id', sa.Uuid(), nullable=True),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('fabricante', sa.String(length=100), nullable=True),
        sa.Column('modelo', sa.String(length=100), nullable=True),
        sa.Column('unidad_medida', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorias_articulos.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_articulos_catalogo_empresa_categoria', 'articulos_catalogo', ['empresa_id', 'categoria_id'], unique=False)
    op.create_index(op.f('ix_articulos_catalogo_empresa_id'), 'articulos_catalogo', ['empresa_id'], unique=False)

    # Crear activos
    op.create_table('activos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('empresa_id', sa.Uuid(), nullable=False),
        sa.Column('articulo_id', sa.Uuid(), nullable=False),
        sa.Column('ubicacion_id', sa.Uuid(), nullable=True),
        sa.Column('serial_interno', sa.String(length=100), nullable=False),
        sa.Column('codigo_activo', sa.String(length=100), nullable=False),
        sa.Column('estado', sa.Enum('operativo', 'en_mantenimiento', 'fuera_de_servicio', 'dado_de_baja', name='assetstatus'), nullable=False),
        sa.Column('fecha_adquisicion', sa.Date(), nullable=True),
        sa.Column('valor_monetario', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('moneda', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['articulo_id'], ['articulos_catalogo.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ubicacion_id'], ['ubicaciones.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('empresa_id', 'codigo_activo', name='uq_activos_empresa_codigo_activo'),
        sa.UniqueConstraint('empresa_id', 'serial_interno', name='uq_activos_empresa_serial_interno')
    )
    op.create_index(op.f('ix_activos_empresa_id'), 'activos', ['empresa_id'], unique=False)


def downgrade() -> None:
    op.drop_table('activos')
    op.drop_table('articulos_catalogo')
    op.drop_table('categorias_articulos')
    op.drop_table('ubicaciones')
    op.drop_table('permisos')
    op.drop_table('roles_usuarios')
    op.drop_table('roles')
    op.drop_table('usuarios')
    op.drop_table('empresas')
    op.drop_table('planes_suscripcion')
