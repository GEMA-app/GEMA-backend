"""0001_initial_schema

Migración consolidad/squash inicial para el sistema GEMA.
Crea las 24 tablas en el orden correcto de dependencias y los enums de base de datos correspondientes.

Revision ID: e4a7b4eca0ab
Revises: None
Create Date: 2026-06-28 12:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e4a7b4eca0ab"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ─── ENUMS ──────────────────────────────────────────────────
    estado_activo = postgresql.ENUM(
        "operativo", "en_mantenimiento", "fuera_de_servicio", "dado_de_baja", name="estado_activo"
    )
    estado_activo.create(op.get_bind(), checkfirst=True)

    tipo_mantenimiento = postgresql.ENUM(
        "preventivo", "correctivo", "predictivo", name="tipo_mantenimiento"
    )
    tipo_mantenimiento.create(op.get_bind(), checkfirst=True)

    estado_orden_trabajo = postgresql.ENUM(
        "abierta", "en_proceso", "pausada", "cerrada", "cancelada", name="estado_orden_trabajo"
    )
    estado_orden_trabajo.create(op.get_bind(), checkfirst=True)

    tipo_ubicacion = postgresql.ENUM(
        "sede", "planta", "area", "seccion", name="tipo_ubicacion"
    )
    tipo_ubicacion.create(op.get_bind(), checkfirst=True)

    modulo_permiso = postgresql.ENUM(
        "activos", "mantenimiento", "inventario", "reportes", "administracion", "preferencias", "system_audit", name="modulo_permiso"
    )
    modulo_permiso.create(op.get_bind(), checkfirst=True)

    estado_empresa = postgresql.ENUM(
        "activa", "suspendida", "cancelada", name="estado_empresa"
    )
    estado_empresa.create(op.get_bind(), checkfirst=True)

    prioridad_nivel = postgresql.ENUM(
        "critica", "alta", "media", "baja", name="prioridad_nivel"
    )
    prioridad_nivel.create(op.get_bind(), checkfirst=True)

    estado_reporte = postgresql.ENUM(
        "pendiente", "en_proceso", "atendido", "descartado", name="estado_reporte"
    )
    estado_reporte.create(op.get_bind(), checkfirst=True)

    # ─── TABLAS ─────────────────────────────────────────────────

    # 1. planes_suscripcion
    op.create_table(
        "planes_suscripcion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("max_activos", sa.Integer(), nullable=True),
        sa.Column("max_usuarios", sa.Integer(), nullable=True),
        sa.Column("precio_mensual_usd", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre")
    )

    # 2. empresas
    op.create_table(
        "empresas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=True),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(63), nullable=False),
        sa.Column("rif", sa.String(50), nullable=True),
        sa.Column("email_contacto", sa.String(255), nullable=True),
        sa.Column("estado", postgresql.ENUM(name="estado_empresa", create_type=False), nullable=False, server_default="activa"),
        sa.Column("trial_hasta", sa.Date(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["plan_id"], ["planes_suscripcion.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_empresas_slug", "empresas", ["slug"], unique=True)

    # 3. usuarios
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("telefono", sa.String(50), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "email", name="uq_usuarios_empresa_email")
    )
    op.create_index("ix_usuarios_empresa_id", "usuarios", ["empresa_id"])

    # 4. roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "nombre", name="uq_roles_empresa_nombre")
    )
    op.create_index("ix_roles_empresa_id", "roles", ["empresa_id"])

    # 5. permisos
    op.create_table(
        "permisos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("rol_id", sa.Uuid(), nullable=False),
        sa.Column("modulo", postgresql.ENUM(name="modulo_permiso", create_type=False), nullable=False),
        sa.Column("puede_ver", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("puede_crear", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("puede_editar", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("puede_eliminar", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rol_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "rol_id", "modulo", name="uq_permisos_empresa_rol_modulo")
    )
    op.create_index("ix_permisos_empresa_id", "permisos", ["empresa_id"])

    # 6. roles_usuarios
    op.create_table(
        "roles_usuarios",
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("rol_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["rol_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("usuario_id", "rol_id")
    )

    # 7. preferencias_usuarios
    op.create_table(
        "preferencias_usuarios",
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("tema", sa.String(20), nullable=False, server_default="oscuro"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("usuario_id")
    )
    op.create_index("ix_preferencias_usuarios_empresa_id", "preferencias_usuarios", ["empresa_id"])

    # 8. ubicaciones
    op.create_table(
        "ubicaciones",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("tipo", postgresql.ENUM(name="tipo_ubicacion", create_type=False), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["ubicaciones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_ubicaciones_empresa_id", "ubicaciones", ["empresa_id"])
    op.create_index("idx_ubicaciones_empresa_parent", "ubicaciones", ["empresa_id", "parent_id"])

    # 9. categorias_articulos
    op.create_table(
        "categorias_articulos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "nombre", name="uq_categorias_articulos_empresa_nombre")
    )
    op.create_index("ix_categorias_articulos_empresa_id", "categorias_articulos", ["empresa_id"])

    # 10. articulos_catalogo
    op.create_table(
        "articulos_catalogo",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("categoria_id", sa.Uuid(), nullable=True),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("fabricante", sa.String(100), nullable=True),
        sa.Column("modelo", sa.String(100), nullable=True),
        sa.Column("unidad_medida", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias_articulos.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_articulos_catalogo_empresa_id", "articulos_catalogo", ["empresa_id"])
    op.create_index("idx_articulos_catalogo_empresa_categoria", "articulos_catalogo", ["empresa_id", "categoria_id"])

    # 11. proveedores
    op.create_table(
        "proveedores",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("rif", sa.String(50), nullable=True),
        sa.Column("telefono", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("contacto", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "rif", name="uq_proveedores_empresa_rif")
    )
    op.create_index("ix_proveedores_empresa_id", "proveedores", ["empresa_id"])

    # 12. activos
    op.create_table(
        "activos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("articulo_id", sa.Uuid(), nullable=False),
        sa.Column("ubicacion_id", sa.Uuid(), nullable=True),
        sa.Column("serial_interno", sa.String(100), nullable=False),
        sa.Column("codigo_activo", sa.String(100), nullable=False),
        sa.Column("estado", postgresql.ENUM(name="estado_activo", create_type=False), nullable=False, server_default="operativo"),
        sa.Column("fecha_adquisicion", sa.Date(), nullable=True),
        sa.Column("valor_monetario", sa.Numeric(12, 2), nullable=True),
        sa.Column("moneda", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["articulo_id"], ["articulos_catalogo.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ubicacion_id"], ["ubicaciones.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_activos_empresa_id", "activos", ["empresa_id"])
    op.create_index(
        "uq_activos_empresa_codigo_activo_lower",
        "activos",
        ["empresa_id", sa.text("LOWER(codigo_activo)")],
        unique=True,
    )
    op.create_index(
        "uq_activos_empresa_serial_interno_lower",
        "activos",
        ["empresa_id", sa.text("LOWER(serial_interno)")],
        unique=True,
    )

    # 13. planes_mantenimiento
    op.create_table(
        "planes_mantenimiento",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("activo_id", sa.Uuid(), nullable=False),
        sa.Column("tecnico_responsable_id", sa.Uuid(), nullable=True),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("tipo", postgresql.ENUM(name="tipo_mantenimiento", create_type=False), nullable=False),
        sa.Column("intervalo_dias", sa.Integer(), nullable=False),
        sa.Column("proxima_ejecucion", sa.Date(), nullable=False),
        sa.Column("descripcion_tareas", sa.Text(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["activo_id"], ["activos.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tecnico_responsable_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_planes_mantenimiento_empresa_id", "planes_mantenimiento", ["empresa_id"])
    op.create_index("ix_planes_mantenimiento_empresa_activo", "planes_mantenimiento", ["empresa_id", "activo_id"])

    # 14. reportes_fallas
    op.create_table(
        "reportes_fallas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("priority", postgresql.ENUM(name="prioridad_nivel", create_type=False), nullable=False, server_default="media"),
        sa.Column("reported_by", sa.String(255), nullable=False),
        sa.Column("status", postgresql.ENUM(name="estado_reporte", create_type=False), nullable=False, server_default="pendiente"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_reportes_fallas_empresa_id", "reportes_fallas", ["empresa_id"])

    # 15. ordenes_trabajo
    op.create_table(
        "ordenes_trabajo",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("codigo_ot", sa.String(30), nullable=False),
        sa.Column("activo_id", sa.Uuid(), nullable=False),
        sa.Column("reporte_id", sa.Uuid(), nullable=True),
        sa.Column("plan_id", sa.Uuid(), nullable=True),
        sa.Column("supervisor_id", sa.Uuid(), nullable=True),
        sa.Column("tipo", postgresql.ENUM(name="tipo_mantenimiento", create_type=False), nullable=False),
        sa.Column("estado", postgresql.ENUM(name="estado_orden_trabajo", create_type=False), nullable=False, server_default="abierta"),
        sa.Column("fecha_apertura", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_inicio_trabajo", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fecha_cierre", sa.DateTime(timezone=True), nullable=True),
        sa.Column("descripcion_trabajo", sa.Text(), nullable=True),
        sa.Column("costo_estimado", sa.Numeric(12, 2), nullable=True),
        sa.Column("costo_real", sa.Numeric(12, 2), nullable=True),
        sa.Column("moneda", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("validado_por_id", sa.Uuid(), nullable=True),
        sa.Column("fecha_validacion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["activo_id"], ["activos.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reporte_id"], ["reportes_fallas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["plan_id"], ["planes_mantenimiento.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["supervisor_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["validado_por_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "codigo_ot", name="uq_ordenes_trabajo_empresa_codigo_ot")
    )
    op.create_index("ix_ordenes_trabajo_empresa_id", "ordenes_trabajo", ["empresa_id"])
    op.create_index("ix_ordenes_trabajo_empresa_activo", "ordenes_trabajo", ["empresa_id", "activo_id"])
    op.create_index("ix_ordenes_trabajo_empresa_estado", "ordenes_trabajo", ["empresa_id", "estado"])

    # 16. tecnicos_ordenes_trabajo
    op.create_table(
        "tecnicos_ordenes_trabajo",
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("ordenes_trabajo_id", sa.Uuid(), nullable=False),
        sa.Column("tecnico_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ordenes_trabajo_id"], ["ordenes_trabajo.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tecnico_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("ordenes_trabajo_id", "tecnico_id")
    )
    op.create_index("ix_tecnicos_ordenes_trabajo_empresa_id", "tecnicos_ordenes_trabajo", ["empresa_id"])

    # 17. intervenciones_tecnicas
    op.create_table(
        "intervenciones_tecnicas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("ordenes_trabajo_id", sa.Uuid(), nullable=False),
        sa.Column("tecnico_id", sa.Uuid(), nullable=False),
        sa.Column("fecha_inicio", sa.DateTime(), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(), nullable=True),
        sa.Column("horas_hombre", sa.Numeric(5, 2), nullable=False),
        sa.Column("tareas_realizadas", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ordenes_trabajo_id"], ["ordenes_trabajo.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tecnico_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_intervenciones_tecnicas_empresa_id", "intervenciones_tecnicas", ["empresa_id"])
    op.create_index("ix_intervenciones_tecnicas_empresa_ot", "intervenciones_tecnicas", ["empresa_id", "ordenes_trabajo_id"])
    op.create_index("ix_intervenciones_tecnicas_empresa_tecnico", "intervenciones_tecnicas", ["empresa_id", "tecnico_id"])

    # 18. inventario_repuestos
    op.create_table(
        "inventario_repuestos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("articulo_id", sa.Uuid(), nullable=False),
        sa.Column("proveedor_id", sa.Uuid(), nullable=True),
        sa.Column("stock_actual", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stock_minimo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ubicacion_almacen", sa.String(255), nullable=True),
        sa.Column("precio_unitario", sa.Numeric(12, 2), nullable=True),
        sa.Column("moneda", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["articulo_id"], ["articulos_catalogo.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["proveedor_id"], ["proveedores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_inventario_repuestos_empresa_id", "inventario_repuestos", ["empresa_id"])
    op.create_index("ix_inventario_repuestos_empresa_articulo", "inventario_repuestos", ["empresa_id", "articulo_id"])

    # 19. repuestos_utilizados
    op.create_table(
        "repuestos_utilizados",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("intervencion_id", sa.Uuid(), nullable=False),
        sa.Column("repuesto_id", sa.Uuid(), nullable=False),
        sa.Column("cantidad_usada", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(12, 2), nullable=True),
        sa.Column("moneda", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["intervencion_id"], ["intervenciones_tecnicas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repuesto_id"], ["inventario_repuestos.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_repuestos_utilizados_empresa_id", "repuestos_utilizados", ["empresa_id"])
    op.create_index("ix_repuestos_utilizados_empresa_intervencion", "repuestos_utilizados", ["empresa_id", "intervencion_id"])
    op.create_index("ix_repuestos_utilizados_empresa_repuesto", "repuestos_utilizados", ["empresa_id", "repuesto_id"])

    # 20. entradas_inventario
    op.create_table(
        "entradas_inventario",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("repuesto_id", sa.Uuid(), nullable=False),
        sa.Column("ordenes_trabajo_id", sa.Uuid(), nullable=True),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("tipo_movimiento", sa.String(50), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(12, 2), nullable=True),
        sa.Column("moneda", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("fecha_movimiento", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ordenes_trabajo_id"], ["ordenes_trabajo.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["repuesto_id"], ["inventario_repuestos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_entradas_inventario_empresa_id", "entradas_inventario", ["empresa_id"])
    op.create_index("ix_entradas_inventario_empresa_repuesto", "entradas_inventario", ["empresa_id", "repuesto_id"])
    op.create_index("ix_entradas_inventario_empresa_ot", "entradas_inventario", ["empresa_id", "ordenes_trabajo_id"])

    # 21. logs_estados_activos
    op.create_table(
        "logs_estados_activos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("activo_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("estado_anterior", postgresql.ENUM(name="estado_activo", create_type=False), nullable=True),
        sa.Column("estado_nuevo", postgresql.ENUM(name="estado_activo", create_type=False), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.Column("fecha_cambio", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["activo_id"], ["activos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_logs_estados_activos_empresa_id", "logs_estados_activos", ["empresa_id"])
    op.create_index("ix_logs_estados_activos_activo_id", "logs_estados_activos", ["activo_id"])
    op.create_index("ix_logs_estados_activos_empresa_activo", "logs_estados_activos", ["empresa_id", "activo_id"])

    # 22. logs_estados_ordenes_trabajo
    op.create_table(
        "logs_estados_ordenes_trabajo",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("ordenes_trabajo_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("estado_anterior", postgresql.ENUM(name="estado_orden_trabajo", create_type=False), nullable=True),
        sa.Column("estado_nuevo", postgresql.ENUM(name="estado_orden_trabajo", create_type=False), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.Column("fecha_cambio", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ordenes_trabajo_id"], ["ordenes_trabajo.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_logs_estados_ordenes_trabajo_empresa_id", "logs_estados_ordenes_trabajo", ["empresa_id"])
    op.create_index("ix_logs_estados_ot_empresa_ot", "logs_estados_ordenes_trabajo", ["empresa_id", "ordenes_trabajo_id"])

    # 23. planes_ejecuciones
    op.create_table(
        "planes_ejecuciones",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("ordenes_trabajo_id", sa.Uuid(), nullable=False),
        sa.Column("fecha_ejecucion", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ordenes_trabajo_id"], ["ordenes_trabajo.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["planes_mantenimiento.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_planes_ejecuciones_empresa_id", "planes_ejecuciones", ["empresa_id"])
    op.create_index("ix_planes_ejecuciones_empresa_plan", "planes_ejecuciones", ["empresa_id", "plan_id"])
    op.create_index("ix_planes_ejecuciones_empresa_ot", "planes_ejecuciones", ["empresa_id", "ordenes_trabajo_id"])

    # 24. auditorias_sistema
    op.create_table(
        "auditorias_sistema",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("accion", sa.String(length=255), nullable=False),
        sa.Column("detalles", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("ocurrido_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_auditorias_sistema_empresa_id", "auditorias_sistema", ["empresa_id"])
    op.create_index("ix_auditorias_sistema_empresa_usuario", "auditorias_sistema", ["empresa_id", "usuario_id"])
    op.create_index("ix_auditorias_sistema_empresa_ocurrido", "auditorias_sistema", ["empresa_id", "ocurrido_en"])


def downgrade() -> None:
    # Eliminación en orden inverso para respetar FKs
    op.drop_table("auditorias_sistema")
    op.drop_table("planes_ejecuciones")
    op.drop_table("logs_estados_ordenes_trabajo")
    op.drop_table("logs_estados_activos")
    op.drop_table("entradas_inventario")
    op.drop_table("repuestos_utilizados")
    op.drop_table("inventario_repuestos")
    op.drop_table("intervenciones_tecnicas")
    op.drop_table("tecnicos_ordenes_trabajo")
    op.drop_table("ordenes_trabajo")
    op.drop_table("reportes_fallas")
    op.drop_table("planes_mantenimiento")
    sa.Enum(name="estado_reporte").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="prioridad_nivel").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="estado_orden_trabajo").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="tipo_mantenimiento").drop(op.get_bind(), checkfirst=True)

    op.drop_table("activos")
    sa.Enum(name="estado_activo").drop(op.get_bind(), checkfirst=True)

    op.drop_table("proveedores")
    op.drop_table("articulos_catalogo")
    op.drop_table("categorias_articulos")
    op.drop_table("ubicaciones")
    sa.Enum(name="tipo_ubicacion").drop(op.get_bind(), checkfirst=True)

    op.drop_table("preferencias_usuarios")
    op.drop_table("roles_usuarios")
    op.drop_table("permisos")
    sa.Enum(name="modulo_permiso").drop(op.get_bind(), checkfirst=True)

    op.drop_table("roles")
    op.drop_table("usuarios")
    op.drop_table("empresas")
    sa.Enum(name="estado_empresa").drop(op.get_bind(), checkfirst=True)

    op.drop_table("planes_suscripcion")
