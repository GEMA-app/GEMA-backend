# migrations/seeds/development.py
"""Seed de desarrollo: 2 empresas demo con datos realistas para desarrollo, testing y staging.

Idempotente: ejecutable múltiples veces sin duplicar registros.
"""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from app.domain.entities import Asset, Company, Location, Permission, Role, User, UserPreference
from app.domain.enums import (
    AssetStatus,
    CompanyStatus,
    LocationType,
    MaintenanceType,
    PermissionModule,
    PriorityLevel,
    ReportStatus,
    Theme,
    WorkOrderStatus,
)
from app.domain.value_objects import CompanyId, Email, HashedPassword, Slug
from app.infrastructure.db.models import ArticleCategoryModel, CatalogArticleModel
from app.infrastructure.db.models.failure_report import FailureReportModel
from app.infrastructure.db.models.inventory_entry import InventoryEntryModel
from app.infrastructure.db.models.inventory_part import InventoryPartModel
from app.infrastructure.db.models.maintenance_plan import MaintenancePlanModel
from app.infrastructure.db.models.plan_execution import PlanExecutionModel
from app.infrastructure.db.models.subscription_plan import SubscriptionPlanModel
from app.infrastructure.db.models.supplier import SupplierModel
from app.infrastructure.db.models.technical_intervention import TechnicalInterventionModel
from app.infrastructure.db.models.used_part import UsedPartModel
from app.infrastructure.db.models.work_order import (
    WorkOrderModel,
    WorkOrderStatusLogModel,
    WorkOrderTechnicianModel,
)
from app.infrastructure.events.bus import InProcessEventBus
from app.infrastructure.security.hashing import BcryptPasswordHasher
from app.infrastructure.uow import SqlAlchemyUnitOfWork

# ─── CONFIGURACIÓN DE ROLES ───────────────────────────────────

ROLES_CONFIG: dict[str, dict] = {
    "Administrador": {
        "desc": "Acceso completo a todos los módulos del sistema",
        "permisos": {
            PermissionModule.ASSETS: (True, True, True, True),
            PermissionModule.MAINTENANCE: (True, True, True, True),
            PermissionModule.INVENTORY: (True, True, True, True),
            PermissionModule.REPORTS: (True, True, True, True),
            PermissionModule.ADMIN: (True, True, True, True),
            PermissionModule.PREFERENCES: (True, False, True, False),
        },
    },
    "Supervisor de Activos": {
        "desc": "Gestiona activos y supervisa su ciclo de vida",
        "permisos": {
            PermissionModule.ASSETS: (True, True, True, False),
            PermissionModule.MAINTENANCE: (True, False, False, False),
            PermissionModule.INVENTORY: (True, False, False, False),
            PermissionModule.REPORTS: (True, False, False, False),
            PermissionModule.ADMIN: (False, False, False, False),
            PermissionModule.PREFERENCES: (True, False, True, False),
        },
    },
    "Técnico de Mantenimiento": {
        "desc": "Ejecuta y registra mantenimiento de activos",
        "permisos": {
            PermissionModule.ASSETS: (True, False, False, False),
            PermissionModule.MAINTENANCE: (True, True, True, False),
            PermissionModule.INVENTORY: (True, False, False, False),
            PermissionModule.REPORTS: (True, True, False, False),
            PermissionModule.ADMIN: (False, False, False, False),
            PermissionModule.PREFERENCES: (True, False, True, False),
        },
    },
    "Almacenista": {
        "desc": "Gestiona inventario y catálogo de artículos",
        "permisos": {
            PermissionModule.ASSETS: (True, False, False, False),
            PermissionModule.MAINTENANCE: (False, False, False, False),
            PermissionModule.INVENTORY: (True, True, True, True),
            PermissionModule.REPORTS: (True, False, False, False),
            PermissionModule.ADMIN: (False, False, False, False),
            PermissionModule.PREFERENCES: (True, False, True, False),
        },
    },
    "Supervisor de Operaciones": {
        "desc": "Supervisa operaciones diarias y genera reportes",
        "permisos": {
            PermissionModule.ASSETS: (True, False, False, False),
            PermissionModule.MAINTENANCE: (True, True, True, True),
            PermissionModule.INVENTORY: (True, True, True, True),
            PermissionModule.REPORTS: (True, True, True, True),
            PermissionModule.ADMIN: (True, False, False, False),
            PermissionModule.PREFERENCES: (True, False, True, False),
        },
    },
    "Consultor (Solo Lectura)": {
        "desc": "Acceso de solo lectura a todos los módulos",
        "permisos": {
            PermissionModule.ASSETS: (True, False, False, False),
            PermissionModule.MAINTENANCE: (True, False, False, False),
            PermissionModule.INVENTORY: (True, False, False, False),
            PermissionModule.REPORTS: (True, False, False, False),
            PermissionModule.ADMIN: (True, False, False, False),
            PermissionModule.PREFERENCES: (True, False, True, False),
        },
    },
}

PERSONAL = [
    ("admin@demo.com", "Carlos Méndez", "Administrador"),
    ("supervisor@demo.com", "María González", "Supervisor de Activos"),
    ("tecnico@demo.com", "Pedro Hernández", "Técnico de Mantenimiento"),
    ("almacen@demo.com", "Ana Rodríguez", "Almacenista"),
    ("operaciones@demo.com", "Luis Martínez", "Supervisor de Operaciones"),
    ("consulta@demo.com", "Sofía López", "Consultor (Solo Lectura)"),
]

# ─── DATOS DE CATÁLOGO ────────────────────────────────────────

CATEGORIAS = [
    {
        "nombre": "Equipos Rotativos",
        "descripcion": "Motores, bombas, turbinas y maquinaria rotativa",
        "articulos": [
            ("Motor Eléctrico trifásico 5HP", "Motor eléctrico WEG W22 Premium IP55", "WEG", "W22 5HP", "unidad"),
            ("Motor Eléctrico trifásico 10HP", "Motor eléctrico WEG W22 Premium IP55 10HP", "WEG", "W22 10HP", "unidad"),
            ("Bomba Centrífuga 2HP", "Bomba centrífuga horizontal Goulds 2HP", "Goulds", "GLC-2H", "unidad"),
        ],
    },
    {
        "nombre": "Instrumentación",
        "descripcion": "Sensores, transmisores, medidores y controladores",
        "articulos": [
            ("Transmisor de Presión", "Transmisor de presión Rosemount 3051S", "Rosemount", "3051S", "unidad"),
            ("Sensor de Temperatura PT100", "Sensor RTD PT100 con cabezal", "Omega", "PT100-3H", "unidad"),
            ("Manómetro Digital", "Manómetro digital WIKA 0-100 PSI", "WIKA", "DG-100", "unidad"),
        ],
    },
    {
        "nombre": "Eléctricos",
        "descripcion": "Componentes y equipos eléctricos de baja y media tensión",
        "articulos": [
            ("Variador de Frecuencia 5HP", "Variador Allen-Bradley PowerFlex 525 5HP", "Allen-Bradley", "PF525-5HP", "unidad"),
            ("Contactor 3 polos 40A", "Contactor Schneider Electric LC1D40", "Schneider", "LC1D40", "unidad"),
        ],
    },
]

# ─── DATOS DE UBICACIONES (ACME) ──────────────────────────────

UBICACIONES_ACME = [
    {
        "nombre": "Sede Principal GEMA",
        "tipo": LocationType.HEADQUARTERS,
        "parent": None,
        "desc": "Sede corporativa y operativa principal",
        "hijos": [
            {
                "nombre": "Planta de Producción A",
                "tipo": LocationType.PLANT,
                "desc": "Línea de montaje y empaque",
                "hijos": [
                    {
                        "nombre": "Área de Compresores",
                        "tipo": LocationType.AREA,
                        "desc": "Sistema neumático central",
                        "hijos": [
                            {"nombre": "Línea de Control de Válvulas", "tipo": LocationType.SECTION, "desc": "Sub-sistema de regulación de presión", "hijos": []},
                        ],
                    },
                    {
                        "nombre": "Área de Ensamble",
                        "tipo": LocationType.AREA,
                        "desc": "Línea de producción principal",
                        "hijos": [
                            {"nombre": "Estación de Trabajo 1", "tipo": LocationType.SECTION, "desc": "Punto de ensamble de motores", "hijos": []},
                            {"nombre": "Estación de Pruebas", "tipo": LocationType.SECTION, "desc": "Pruebas de calidad y funcionamiento", "hijos": []},
                        ],
                    },
                ],
            },
            {
                "nombre": "Planta de Almacenamiento",
                "tipo": LocationType.PLANT,
                "desc": "Centro de logística y almacén",
                "hijos": [
                    {
                        "nombre": "Almacén de Insumos",
                        "tipo": LocationType.AREA,
                        "desc": "Recepción y almacenamiento de materia prima",
                        "hijos": [],
                    },
                    {
                        "nombre": "Almacén de Repuestos",
                        "tipo": LocationType.AREA,
                        "desc": "Inventario de repuestos y componentes",
                        "hijos": [],
                    },
                ],
            },
        ],
    },
]

# ─── DATOS DE ACTIVOS ─────────────────────────────────────────

ACTIVOS_ACME = [
    {
        "articulo_nombre": "Motor Eléctrico trifásico 5HP",
        "serial": "SN-WEG-5HP-001",
        "codigo": "ACT-MOT-001",
        "estado": AssetStatus.OPERATIONAL,
        "fecha": date(2026, 1, 15),
        "valor": Decimal("450.00"),
        "ubicacion": "Línea de Control de Válvulas",
    },
    {
        "articulo_nombre": "Motor Eléctrico trifásico 10HP",
        "serial": "SN-WEG-10HP-002",
        "codigo": "ACT-MOT-002",
        "estado": AssetStatus.OPERATIONAL,
        "fecha": date(2026, 2, 20),
        "valor": Decimal("850.00"),
        "ubicacion": "Estación de Trabajo 1",
    },
    {
        "articulo_nombre": "Bomba Centrífuga 2HP",
        "serial": "SN-GOU-2H-003",
        "codigo": "ACT-BOM-001",
        "estado": AssetStatus.UNDER_MAINTENANCE,
        "fecha": date(2025, 11, 10),
        "valor": Decimal("320.00"),
        "ubicacion": "Área de Compresores",
    },
    {
        "articulo_nombre": "Transmisor de Presión",
        "serial": "SN-ROS-3051-004",
        "codigo": "ACT-TRN-001",
        "estado": AssetStatus.OPERATIONAL,
        "fecha": date(2026, 3, 5),
        "valor": Decimal("1250.00"),
        "ubicacion": "Línea de Control de Válvulas",
    },
    {
        "articulo_nombre": "Sensor de Temperatura PT100",
        "serial": "SN-OMG-PT100-005",
        "codigo": "ACT-SEN-001",
        "estado": AssetStatus.OUT_OF_SERVICE,
        "fecha": date(2024, 6, 1),
        "valor": Decimal("85.00"),
        "ubicacion": "Estación de Pruebas",
    },
    {
        "articulo_nombre": "Variador de Frecuencia 5HP",
        "serial": "SN-AB-PF525-006",
        "codigo": "ACT-VFD-001",
        "estado": AssetStatus.OPERATIONAL,
        "fecha": date(2026, 4, 12),
        "valor": Decimal("2200.00"),
        "ubicacion": "Área de Compresores",
    },
]

# ─── EMPRESA B (multi-tenant) ─────────────────────────────────

PERSONAL_EMPRESA_B = [
    ("admin@industriasbeta.com", "Roberto Vega", "Administrador"),
    ("consulta@industriasbeta.com", "Elena Rivas", "Consultor (Solo Lectura)"),
]

ACTIVOS_EMPRESA_B = [
    {
        "articulo_nombre": "Contactor 3 polos 40A",
        "serial": "SN-SCH-LC1D40-B01",
        "codigo": "B-ACT-ELC-001",
        "estado": AssetStatus.OPERATIONAL,
        "fecha": date(2026, 5, 1),
        "valor": Decimal("180.00"),
    },
    {
        "articulo_nombre": "Manómetro Digital",
        "serial": "SN-WIKA-DG-B02",
        "codigo": "B-ACT-INS-001",
        "estado": AssetStatus.OPERATIONAL,
        "fecha": date(2026, 5, 15),
        "valor": Decimal("320.00"),
    },
]

# ─── PROVEEDORES (ACME) ──────────────────────────────────────

SUPPLIERS_ACME = [
    {"nombre": "Suministros Industriales WEG C.A.", "rif": "J-40012345-6", "telefono": "+58-212-555-0101", "email": "ventas@weg.co.ve", "contacto": "Pedro Torres"},
    {"nombre": "Instrumentación Rosemount S.A.S.", "rif": "J-40067890-1", "telefono": "+58-241-555-0202", "email": "ventas@rosemount.com", "contacto": "Laura Méndez"},
    {"nombre": "Distribuidora Eléctrica Schneider", "rif": "J-40011223-4", "telefono": "+58-212-555-0303", "email": "ventas@schneider.co.ve", "contacto": "Carlos Ruiz"},
    {"nombre": "Omega Instruments C.A.", "rif": "J-40099887-5", "telefono": "+58-261-555-0404", "email": "ventas@omega.co.ve", "contacto": "Ana Soto"},
]

# ─── REPORTES DE FALLA (ACME) ───────────────────────────────

REPORTES_FALLA_ACME = [
    {"title": "Vibración anormal en Motor 5HP", "description": "El motor de la línea de control presenta vibraciones excesivas en el eje principal. Posible desbalanceo o desgaste de rodamientos.", "location": "Línea de Control de Válvulas", "priority": PriorityLevel.HIGH, "activo_codigo": "ACT-MOT-001", "status": ReportStatus.IN_PROGRESS},
    {"title": "Fuga de refrigerante en bomba centrífuga", "description": "La bomba del área de compresores presenta fuga de refrigerante por el sello mecánico. Requiere reemplazo.", "location": "Área de Compresores", "priority": PriorityLevel.CRITICAL, "activo_codigo": "ACT-BOM-001", "status": ReportStatus.PENDING},
    {"title": "Lecturas erráticas en transmisor de presión", "description": "El transmisor 3051S muestra lecturas intermitentes. Se observa corrosión en el conector.", "location": "Línea de Control de Válvulas", "priority": PriorityLevel.MEDIUM, "activo_codigo": "ACT-TRN-001", "status": ReportStatus.RESOLVED},
    {"title": "Sensor PT100 sin señal", "description": "El sensor de temperatura en la estación de pruebas no reporta señal. Posible cableado dañado.", "location": "Estación de Pruebas", "priority": PriorityLevel.LOW, "activo_codigo": "ACT-SEN-001", "status": ReportStatus.PENDING},
]

# ─── ÓRDENES DE TRABAJO (ACME) ──────────────────────────────

OT_ACME = [
    {
        "codigo": "OT-2026-001",
        "activo_codigo": "ACT-MOT-001",
        "tipo": MaintenanceType.CORRECTIVE,
        "estado": WorkOrderStatus.IN_PROGRESS,
        "descripcion": "Diagnóstico y corrección de vibraciones en motor 5HP de la línea de válvulas",
        "tecnico_email": "tecnico@demo.com",
        "supervisor_email": "supervisor@demo.com",
        "log_estados": [
            ("abierta", "tecnico@demo.com", "Se asigna técnico para diagnóstico inicial"),
            ("en_proceso", "tecnico@demo.com", "Inicio de trabajos de diagnóstico"),
        ],
    },
    {
        "codigo": "OT-2026-002",
        "activo_codigo": "ACT-BOM-001",
        "tipo": MaintenanceType.CORRECTIVE,
        "estado": WorkOrderStatus.OPEN,
        "descripcion": "Reemplazo de sello mecánico en bomba centrífuga 2HP",
        "tecnico_email": "tecnico@demo.com",
        "supervisor_email": "supervisor@demo.com",
        "log_estados": [],
    },
    {
        "codigo": "OT-2026-003",
        "activo_codigo": "ACT-TRN-001",
        "tipo": MaintenanceType.PREVENTIVE,
        "estado": WorkOrderStatus.CLOSED,
        "descripcion": "Revisión y calibración de transmisor de presión: lecturas normalizadas",
        "tecnico_email": "tecnico@demo.com",
        "supervisor_email": "supervisor@demo.com",
        "log_estados": [
            ("abierta", "supervisor@demo.com", "OT creada para mantenimiento preventivo"),
            ("en_proceso", "tecnico@demo.com", "Inicio de trabajos"),
            ("cerrada", "tecnico@demo.com", "Trabajos completados, activo operativo"),
        ],
    },
]

# ─── PASSWORD HASH CACHE ─────────────────────────────────────

_PASSWORD_HASH: str = ""


def _get_password_hash() -> str:
    global _PASSWORD_HASH
    if not _PASSWORD_HASH:
        hasher = BcryptPasswordHasher()
        _PASSWORD_HASH = hasher.hash("Password123!")
    return _PASSWORD_HASH


# ─── HELPERS ──────────────────────────────────────────────────

def _build_ubicacion(loc_data: dict, empresa_id, parent_id=None, parent_type=None):
    loc = Location.create(
        empresa_id=empresa_id,
        parent_id=parent_id,
        nombre=loc_data["nombre"],
        tipo=loc_data["tipo"],
        parent_type=parent_type,
        descripcion=loc_data["desc"],
    )
    hijos: list[Location] = []
    for child in loc_data.get("hijos", []):
        hijos.extend(_build_ubicacion(child, empresa_id, loc.id, loc_data["tipo"]))
    return [loc] + hijos

# ─── SEED PRINCIPAL ───────────────────────────────────────────

async def seed() -> None:
    """Pobla la base de datos con datos iniciales para desarrollo/testing/staging."""
    uow = SqlAlchemyUnitOfWork(event_bus=InProcessEventBus())
    password_hash = _get_password_hash()

    from sqlalchemy import select

    async with uow:
        # 1. Plan de Suscripción
        stmt_plan = select(SubscriptionPlanModel).where(
            SubscriptionPlanModel.nombre == "Plan Premium GEMA"
        )
        res_plan = await uow.session.execute(stmt_plan)
        plan = res_plan.scalar_one_or_none()
        if not plan:
            plan = SubscriptionPlanModel(
                id=uuid.UUID("d6346dd5-b62a-4aed-bfdb-a9ab1ff8a8b1"),
                nombre="Plan Premium GEMA",
                descripcion="Plan premium con todas las características de la plataforma habilitadas",
                max_activos=100,
                max_usuarios=20,
                precio_mensual_usd=Decimal("99.99"),
            )
            uow.session.add(plan)
            await uow.session.flush()
            print("✅ Plan Premium GEMA creado.")

        # 2. Plan Básico (para empresa B)
        stmt_basic = select(SubscriptionPlanModel).where(
            SubscriptionPlanModel.nombre == "Plan Básico GEMA"
        )
        res_basic = await uow.session.execute(stmt_basic)
        plan_basic = res_basic.scalar_one_or_none()
        if not plan_basic:
            plan_basic = SubscriptionPlanModel(
                id=uuid.UUID("a7b3c9d1-e2f4-4a5b-8c6d-7e8f9a0b1c2d"),
                nombre="Plan Básico GEMA",
                descripcion="Plan básico con funcionalidades limitadas",
                max_activos=20,
                max_usuarios=5,
                precio_mensual_usd=Decimal("29.99"),
            )
            uow.session.add(plan_basic)
            await uow.session.flush()
            print("✅ Plan Básico GEMA creado.")

        # ─── EMPRESA A: ACME S.A. ─────────────────────────────────

        existing_company = await uow.companies.get_by_slug(Slug.from_name("ACME S.A."))
        if existing_company:
            print("ℹ️ Empresa 'ACME S.A.' ya existe. Saltando.")
            company_a = existing_company
        else:
            company_a = Company(
                id=CompanyId(uuid.UUID("8719bfd0-5cfb-4a5d-9f2b-da9ab1ff8a8b")),
                nombre="ACME S.A.",
                slug=Slug.from_name("ACME S.A."),
                rif="J-12345678-9",
                email_contacto="admin@demo.com",
                estado=CompanyStatus.ACTIVE,
                plan_id=plan.id,
            )
            await uow.companies.save(company_a)
            await uow.session.flush()
            print("✅ Empresa 'ACME S.A.' creada.")

        # Roles
        existing_roles = await uow.roles.list_by_company(company_a.id)
        roles_map_a = {r.nombre: r for r in existing_roles}
        for nombre, config in ROLES_CONFIG.items():
            permisos = [
                Permission(module=mod, can_view=v, can_create=c, can_edit=e, can_delete=d)
                for mod, (v, c, e, d) in config["permisos"].items()
            ]
            if nombre in roles_map_a:
                rol = roles_map_a[nombre]
                rol.permisos = permisos
                await uow.roles.save(rol)
            else:
                rol = Role.create(empresa_id=company_a.id, nombre=nombre, descripcion=config["desc"], permisos=permisos)
                await uow.roles.save(rol)
                roles_map_a[nombre] = rol
                print(f"✅ Rol '{nombre}' creado en ACME.")

        # Usuarios ACME
        users_map_a: dict[str, User] = {}
        for email_str, nombre, rol_nombre in PERSONAL:
            email = Email(email_str)
            existing_user = await uow.users.get_by_email(email)
            if existing_user:
                users_map_a[email_str] = existing_user
                continue
            user = User.register(email=email, password_hash=HashedPassword(password_hash), empresa_id=company_a.id, nombre=nombre)
            await uow.users.save(user)
            await uow.session.flush()
            users_map_a[email_str] = user
            rol = roles_map_a[rol_nombre]
            rol.record_assignment(user.id)
            await uow.roles.save(rol)
            await uow.roles.assign_to_user(rol.id, user.id)
            pref = UserPreference.create(usuario_id=user.id, empresa_id=company_a.id, tema=Theme.SYSTEM)
            await uow.preferences.save(pref)
            print(f"✅ Usuario '{email_str}' registrado en ACME con rol '{rol_nombre}'.")

        # Ubicaciones ACME
        all_locs_a: list[Location] = []
        existing_locs_a = await uow.locations.get_tree(company_a.id)
        if existing_locs_a:
            # Reconstruir mapa nombre→Location
            locs_by_name = {}
            stack = list(existing_locs_a)
            while stack:
                loc = stack.pop()
                locs_by_name[loc.nombre] = loc
            all_locs_a = list(existing_locs_a)
        else:
            for sede_data in UBICACIONES_ACME:
                created = _build_ubicacion(sede_data, company_a.id)
                for loc in created:
                    await uow.locations.save(loc)
                    await uow.session.flush()
                all_locs_a.extend(created)
            print("✅ Estructura de ubicaciones ACME creada.")
            # Reconstruir mapa
            locs_by_name = {loc.nombre: loc for loc in all_locs_a}

        # Catálogo ACME
        stmt_cat = select(ArticleCategoryModel).where(ArticleCategoryModel.empresa_id == company_a.id.value)
        res_cat = await uow.session.execute(stmt_cat)
        existing_cats = {c.nombre: c for c in res_cat.scalars().all()}

        articulos_por_nombre = {}
        for cat_def in CATEGORIAS:
            if cat_def["nombre"] in existing_cats:
                cat_model = existing_cats[cat_def["nombre"]]
            else:
                cat_model = ArticleCategoryModel(
                    id=uuid.uuid4(), empresa_id=company_a.id.value,
                    nombre=cat_def["nombre"], descripcion=cat_def["descripcion"],
                )
                uow.session.add(cat_model)
                await uow.session.flush()
                existing_cats[cat_def["nombre"]] = cat_model
                print(f"✅ Categoría '{cat_def['nombre']}' creada en ACME.")

            for art_nombre, art_desc, fab, modelo, udm in cat_def["articulos"]:
                stmt_art = select(CatalogArticleModel).where(
                    CatalogArticleModel.empresa_id == company_a.id.value,
                    CatalogArticleModel.name == art_nombre,
                )
                existing_art = (await uow.session.execute(stmt_art)).scalar_one_or_none()
                if not existing_art:
                    art = CatalogArticleModel(
                        id=uuid.uuid4(), category_id=cat_model.id, empresa_id=company_a.id.value,
                        name=art_nombre, description=art_desc, manufacturer=fab, model=modelo, unit_of_measure=udm,
                    )
                    uow.session.add(art)
                    await uow.session.flush()
                articulos_por_nombre[art_nombre] = art_nombre  # referencia por nombre

        # Activos ACME
        existing_assets_a, _ = await uow.assets.list_by_company(company_a.id, offset=0, limit=100)
        if not existing_assets_a:
            for act_def in ACTIVOS_ACME:
                # Obtener articulo_id
                stmt_art = select(CatalogArticleModel).where(
                    CatalogArticleModel.empresa_id == company_a.id.value,
                    CatalogArticleModel.name == act_def["articulo_nombre"],
                )
                art_model = (await uow.session.execute(stmt_art)).scalar_one_or_none()
                if not art_model:
                    continue
                ubicacion = locs_by_name.get(act_def["ubicacion"])
                if not ubicacion:
                    continue
                asset = Asset.create(
                    empresa_id=company_a.id,
                    articulo_id=art_model.id,
                    ubicacion_id=ubicacion.id,
                    serial_interno=act_def["serial"],
                    codigo_activo=act_def["codigo"],
                    estado=act_def["estado"],
                    fecha_adquisicion=act_def["fecha"],
                    valor_monetario=act_def["valor"],
                    moneda="USD",
                )
                await uow.assets.save(asset)
                await uow.session.flush()
            print(f"✅ {len(ACTIVOS_ACME)} activos creados en ACME.")

        # ─── PROVEEDORES (ACME) ──────────────────────────────────
        existing_suppliers = {}
        stmt_sup = select(SupplierModel).where(SupplierModel.empresa_id == company_a.id.value)
        for s in (await uow.session.execute(stmt_sup)).scalars().all():
            existing_suppliers[s.nombre] = s
        for sd in SUPPLIERS_ACME:
            if sd["nombre"] not in existing_suppliers:
                sup = SupplierModel(
                    id=uuid.uuid4(), empresa_id=company_a.id.value,
                    nombre=sd["nombre"], rif=sd["rif"],
                    telefono=sd["telefono"], email=sd["email"], contacto=sd["contacto"],
                )
                uow.session.add(sup)
                await uow.session.flush()
                existing_suppliers[sd["nombre"]] = sup
                print(f"✅ Proveedor '{sd['nombre']}' creado en ACME.")
        # Mapa: nombre del artículo → proveedor_id
        sup_by_articulo = {
            "Motor Eléctrico trifásico 5HP": existing_suppliers["Suministros Industriales WEG C.A."].id,
            "Motor Eléctrico trifásico 10HP": existing_suppliers["Suministros Industriales WEG C.A."].id,
            "Bomba Centrífuga 2HP": existing_suppliers["Suministros Industriales WEG C.A."].id,
            "Transmisor de Presión": existing_suppliers["Instrumentación Rosemount S.A.S."].id,
            "Sensor de Temperatura PT100": existing_suppliers["Omega Instruments C.A."].id,
            "Manómetro Digital": existing_suppliers["Instrumentación Rosemount S.A.S."].id,
            "Variador de Frecuencia 5HP": existing_suppliers["Distribuidora Eléctrica Schneider"].id,
            "Contactor 3 polos 40A": existing_suppliers["Distribuidora Eléctrica Schneider"].id,
        }

        # ─── INVENTARIO DE REPUESTOS (ACME) ─────────────────────
        stmt_arts = select(CatalogArticleModel).where(CatalogArticleModel.empresa_id == company_a.id.value)
        arts_by_name = {a.name: a for a in (await uow.session.execute(stmt_arts)).scalars().all()}
        stmt_inv = select(InventoryPartModel).where(InventoryPartModel.empresa_id == company_a.id.value)
        existing_inv = {(r.articulo_id, r.proveedor_id) for r in (await uow.session.execute(stmt_inv)).scalars().all()}
        INV_PARTES = [
            ("Motor Eléctrico trifásico 5HP", 5, 2, "Almacén de Repuestos", Decimal("420.00")),
            ("Motor Eléctrico trifásico 10HP", 3, 1, "Almacén de Repuestos", Decimal("800.00")),
            ("Bomba Centrífuga 2HP", 2, 1, "Almacén de Repuestos", Decimal("300.00")),
            ("Transmisor de Presión", 4, 2, "Almacén de Repuestos", Decimal("1180.00")),
            ("Sensor de Temperatura PT100", 10, 3, "Almacén de Repuestos", Decimal("75.00")),
            ("Manómetro Digital", 6, 2, "Almacén de Repuestos", Decimal("310.00")),
            ("Variador de Frecuencia 5HP", 2, 1, "Almacén de Repuestos", Decimal("2050.00")),
            ("Contactor 3 polos 40A", 8, 3, "Almacén de Repuestos", Decimal("165.00")),
        ]
        for art_nombre, stock, min_stock, ubicacion, precio in INV_PARTES:
            art = arts_by_name.get(art_nombre)
            if not art:
                continue
            prov_id = sup_by_articulo.get(art_nombre)
            key = (art.id, prov_id)
            if key not in existing_inv:
                inv = InventoryPartModel(
                    id=uuid.uuid4(), empresa_id=company_a.id.value,
                    articulo_id=art.id, proveedor_id=prov_id,
                    stock_actual=stock, stock_minimo=min_stock,
                    ubicacion_almacen=ubicacion, precio_unitario=precio, moneda="USD",
                )
                uow.session.add(inv)
                await uow.session.flush()
                existing_inv.add(key)
        print(f"✅ {len(INV_PARTES)} repuestos creados en inventario ACME.")

        # ─── ENTRADAS DE INVENTARIO (ACME) ─────────────────────
        stmt_entries = select(InventoryEntryModel).where(InventoryEntryModel.empresa_id == company_a.id.value)
        entry_existing = {e.repuesto_id for e in (await uow.session.execute(stmt_entries)).scalars().all()}
        stmt_parts = select(InventoryPartModel).where(InventoryPartModel.empresa_id == company_a.id.value)
        parts = (await uow.session.execute(stmt_parts)).scalars().all()
        for part in parts:
            if part.id in entry_existing:
                continue
            entry = InventoryEntryModel(
                id=uuid.uuid4(), empresa_id=company_a.id.value,
                repuesto_id=part.id, usuario_id=users_map_a["almacen@demo.com"].id.value,
                cantidad=part.stock_actual, tipo_movimiento="entrada",
                precio_unitario=part.precio_unitario, moneda="USD",
                fecha_movimiento=datetime.now(UTC),
                observaciones="Stock inicial registrado durante configuración del sistema",
            )
            uow.session.add(entry)
            await uow.session.flush()
            entry_existing.add(part.id)
        print(f"✅ {len(parts)} entradas iniciales de inventario creadas en ACME.")

        # ─── Mapa activos ACME por código ───────────────────────
        existing_assets_a, _ = await uow.assets.list_by_company(company_a.id, offset=0, limit=100)
        activos_por_codigo_a = {a.codigo_activo: a for a in existing_assets_a}

        # ─── PLANES DE MANTENIMIENTO (ACME) ────────────────────
        PLANES_ACME = [
            {"nombre": "Plan Preventivo Motor 5HP", "activo_codigo": "ACT-MOT-001", "tipo": MaintenanceType.PREVENTIVE, "intervalo": 90, "proxima": date(2026, 7, 15), "desc": "Lubricación, revisión de rodamientos y alineación del eje cada 90 días", "tecnico_email": "tecnico@demo.com"},
            {"nombre": "Plan Correctivo Bomba Centrífuga", "activo_codigo": "ACT-BOM-001", "tipo": MaintenanceType.CORRECTIVE, "intervalo": 30, "proxima": date(2026, 7, 1), "desc": "Inspección de sellos mecánicos y revisión de impulsor cada 30 días", "tecnico_email": "tecnico@demo.com"},
        ]
        stmt_plan = select(MaintenancePlanModel).where(MaintenancePlanModel.empresa_id == company_a.id.value)
        plan_existing = {p.nombre for p in (await uow.session.execute(stmt_plan)).scalars().all()}
        for pd in PLANES_ACME:
            if pd["nombre"] in plan_existing:
                continue
            activo = activos_por_codigo_a.get(pd["activo_codigo"])
            if not activo:
                continue
            tecnico = users_map_a.get(pd["tecnico_email"])
            plan = MaintenancePlanModel(
                id=uuid.uuid4(), empresa_id=company_a.id.value,
                activo_id=activo.id.value,
                tecnico_responsable_id=tecnico.id.value if tecnico else None,
                nombre=pd["nombre"], tipo=pd["tipo"],
                intervalo_dias=pd["intervalo"], proxima_ejecucion=pd["proxima"],
                descripcion_tareas=pd["desc"], activo=True,
            )
            uow.session.add(plan)
            await uow.session.flush()
            plan_existing.add(pd["nombre"])
            print(f"✅ Plan '{pd['nombre']}' creado en ACME.")

        # ─── REPORTES DE FALLA (ACME) ───────────────────────────
        stmt_rep = select(FailureReportModel).where(FailureReportModel.empresa_id == company_a.id.value)
        rep_existing = {(r.title, r.activo_id) for r in (await uow.session.execute(stmt_rep)).scalars().all()}
        now_ts = datetime.now(UTC)
        for rd in REPORTES_FALLA_ACME:
            activo = activos_por_codigo_a.get(rd["activo_codigo"])
            if not activo:
                continue
            if (rd["title"], activo.id.value) in rep_existing:
                continue
            rep = FailureReportModel(
                id=uuid.uuid4(), empresa_id=company_a.id.value,
                title=rd["title"], description=rd["description"],
                location=rd["location"], priority=rd["priority"],
                reported_by=users_map_a["supervisor@demo.com"].nombre,
                activo_id=activo.id.value, status=rd["status"],
            )
            uow.session.add(rep)
            await uow.session.flush()
            rep_existing.add((rd["title"], activo.id.value))
            print(f"✅ Reporte '{rd['title']}' creado en ACME.")

        # ─── ÓRDENES DE TRABAJO (ACME) ──────────────────────────
        stmt_ot = select(WorkOrderModel).where(WorkOrderModel.empresa_id == company_a.id.value)
        ot_existing = {o.codigo_ot for o in (await uow.session.execute(stmt_ot)).scalars().all()}
        # Traer reportes recién creados
        rep_models = (await uow.session.execute(
            select(FailureReportModel).where(FailureReportModel.empresa_id == company_a.id.value)
        )).scalars().all()
        reporte_por_activo = {r.activo_id: r for r in rep_models if r.activo_id}
        for od in OT_ACME:
            if od["codigo"] in ot_existing:
                continue
            activo = activos_por_codigo_a.get(od["activo_codigo"])
            if not activo:
                continue
            supervisor = users_map_a.get(od["supervisor_email"])
            tecnico = users_map_a.get(od["tecnico_email"])
            reporte = reporte_por_activo.get(activo.id.value)
            ot = WorkOrderModel(
                id=uuid.uuid4(), empresa_id=company_a.id.value,
                codigo_ot=od["codigo"], activo_id=activo.id.value,
                reporte_id=reporte.id if reporte else None,
                supervisor_id=supervisor.id.value if supervisor else None,
                tipo=od["tipo"], estado=od["estado"],
                fecha_apertura=now_ts,
                descripcion_trabajo=od["descripcion"],
                costo_estimado=Decimal("0.00"), moneda="USD",
            )
            uow.session.add(ot)
            await uow.session.flush()
            ot_existing.add(od["codigo"])

            # Asignar técnico
            if tecnico:
                stmt_t = select(WorkOrderTechnicianModel).where(
                    WorkOrderTechnicianModel.ordenes_trabajo_id == ot.id,
                    WorkOrderTechnicianModel.tecnico_id == tecnico.id.value,
                )
                if not (await uow.session.execute(stmt_t)).scalar_one_or_none():
                    uow.session.add(WorkOrderTechnicianModel(
                        ordenes_trabajo_id=ot.id, tecnico_id=tecnico.id.value,
                        empresa_id=company_a.id.value,
                    ))

            # Logs de estado
            for estado_anterior, actor_email, motivo in od["log_estados"]:
                actor = users_map_a.get(actor_email)
                uow.session.add(WorkOrderStatusLogModel(
                    id=uuid.uuid4(), ordenes_trabajo_id=ot.id,
                    empresa_id=company_a.id.value,
                    estado_anterior=None,
                    estado_nuevo=WorkOrderStatus(estado_anterior),
                    usuario_id=actor.id.value if actor else None,
                    motivo=motivo, fecha_cambio=now_ts,
                ))
            await uow.session.flush()
            print(f"✅ OT '{od['codigo']}' creada en ACME.")

        # ─── INTERVENCIONES TÉCNICAS (ACME) ────────────────────
        all_ots = (await uow.session.execute(
            select(WorkOrderModel).where(WorkOrderModel.empresa_id == company_a.id.value)
        )).scalars().all()
        it_existing = {(i.ordenes_trabajo_id, i.tecnico_id) for i in (await uow.session.execute(
            select(TechnicalInterventionModel).where(TechnicalInterventionModel.empresa_id == company_a.id.value)
        )).scalars().all()}
        for ot in all_ots:
            if ot.estado != WorkOrderStatus.CLOSED:
                continue
            tecnico = users_map_a.get("tecnico@demo.com")
            key = (ot.id, tecnico.id.value)
            if key in it_existing:
                continue
            interv = TechnicalInterventionModel(
                id=uuid.uuid4(), empresa_id=company_a.id.value,
                ordenes_trabajo_id=ot.id, tecnico_id=tecnico.id.value,
                fecha_inicio=datetime(2026, 6, 10, 8, 0),
                fecha_fin=datetime(2026, 6, 10, 14, 30),
                horas_hombre=Decimal("6.50"),
                tareas_realizadas="Revisión de conexiones, calibración del transmisor y pruebas funcionales. Lecturas normalizadas.",
            )
            uow.session.add(interv)
            await uow.session.flush()
            print(f"✅ Intervención sobre OT '{ot.codigo_ot}' creada en ACME.")

        # ─── REPUESTOS UTILIZADOS (ACME) ──────────────────────
        intervs = (await uow.session.execute(
            select(TechnicalInterventionModel).where(TechnicalInterventionModel.empresa_id == company_a.id.value)
        )).scalars().all()
        used_existing = {(u.intervencion_id, u.repuesto_id) for u in (await uow.session.execute(
            select(UsedPartModel).where(UsedPartModel.empresa_id == company_a.id.value)
        )).scalars().all()}
        for iv in intervs:
            stmt_art = select(CatalogArticleModel).where(
                CatalogArticleModel.empresa_id == company_a.id.value,
                CatalogArticleModel.name == "Transmisor de Presión",
            )
            art = (await uow.session.execute(stmt_art)).scalar_one_or_none()
            if not art:
                continue
            stmt_part = select(InventoryPartModel).where(
                InventoryPartModel.empresa_id == company_a.id.value,
                InventoryPartModel.articulo_id == art.id,
            )
            part = (await uow.session.execute(stmt_part)).scalar_one_or_none()
            if not part:
                continue
            key = (iv.id, part.id)
            if key in used_existing:
                continue
            uow.session.add(UsedPartModel(
                id=uuid.uuid4(), empresa_id=company_a.id.value,
                intervencion_id=iv.id, repuesto_id=part.id,
                cantidad_usada=1, precio_unitario=part.precio_unitario, moneda="USD",
            ))
            part.stock_actual -= 1
            uow.session.add(part)
            await uow.session.flush()
            used_existing.add(key)
            print(f"✅ 1 '{art.name}' consumido en intervención, stock restante: {part.stock_actual}.")

        # ─── EJECUCIONES DE PLAN (ACME) ───────────────────────
        planes = (await uow.session.execute(
            select(MaintenancePlanModel).where(MaintenancePlanModel.empresa_id == company_a.id.value)
        )).scalars().all()
        ots_por_activo = {o.activo_id: o for o in (await uow.session.execute(
            select(WorkOrderModel).where(WorkOrderModel.empresa_id == company_a.id.value)
        )).scalars().all()}
        exec_existing = {(e.plan_id, e.work_order_id) for e in (await uow.session.execute(
            select(PlanExecutionModel).where(PlanExecutionModel.empresa_id == company_a.id.value)
        )).scalars().all()}
        for plan in planes:
            ot = ots_por_activo.get(plan.activo_id)
            if not ot:
                continue
            key = (plan.id, ot.id)
            if key in exec_existing:
                continue
            uow.session.add(PlanExecutionModel(
                id=uuid.uuid4(), empresa_id=company_a.id.value,
                plan_id=plan.id, work_order_id=ot.id,
                execution_date=datetime.now(UTC),
                observations="Ejecución inicial del plan de mantenimiento",
            ))
            await uow.session.flush()
            exec_existing.add(key)
            print(f"✅ Ejecución del plan '{plan.nombre}' asociada a OT '{ot.codigo_ot}'.")

        # ─── EMPRESA B: Industrias Beta (multi-tenant) ─────────────

        existing_company_b = await uow.companies.get_by_slug(Slug.from_name("Industrias Beta"))
        if existing_company_b:
            print("ℹ️ Empresa 'Industrias Beta' ya existe. Saltando.")
            company_b = existing_company_b
        else:
            company_b = Company(
                id=CompanyId(uuid.UUID("2a3b4c5d-6e7f-8a9b-0c1d-2e3f4a5b6c7d")),
                nombre="Industrias Beta",
                slug=Slug.from_name("Industrias Beta"),
                rif="J-98765432-1",
                email_contacto="admin@industriasbeta.com",
                estado=CompanyStatus.ACTIVE,
                plan_id=plan_basic.id,
            )
            await uow.companies.save(company_b)
            await uow.session.flush()
            print("✅ Empresa 'Industrias Beta' creada.")

        # Roles empresa B (Administrador + Consultor)
        existing_roles_b = await uow.roles.list_by_company(company_b.id)
        roles_map_b = {r.nombre: r for r in existing_roles_b}
        for nombre in ("Administrador", "Consultor (Solo Lectura)"):
            if nombre not in roles_map_b:
                cfg = ROLES_CONFIG[nombre]
                rol = Role.create(
                    empresa_id=company_b.id, nombre=nombre, descripcion=cfg["desc"],
                    permisos=[Permission(module=mod, can_view=v, can_create=c, can_edit=e, can_delete=d)
                              for mod, (v, c, e, d) in cfg["permisos"].items()],
                )
                await uow.roles.save(rol)
                roles_map_b[nombre] = rol
                print(f"✅ Rol '{nombre}' creado en Industrias Beta.")

        # Usuarios empresa B
        users_map_b: dict[str, User] = {}
        for email_str, nombre, rol_nombre in PERSONAL_EMPRESA_B:
            email = Email(email_str)
            existing_user = await uow.users.get_by_email(email)
            if existing_user:
                users_map_b[email_str] = existing_user
                continue
            user = User.register(email=email, password_hash=HashedPassword(password_hash), empresa_id=company_b.id, nombre=nombre)
            await uow.users.save(user)
            await uow.session.flush()
            users_map_b[email_str] = user
            rol = roles_map_b[rol_nombre]
            rol.record_assignment(user.id)
            await uow.roles.save(rol)
            await uow.roles.assign_to_user(rol.id, user.id)
            pref = UserPreference.create(usuario_id=user.id, empresa_id=company_b.id, tema=Theme.SYSTEM)
            await uow.preferences.save(pref)
            print(f"✅ Usuario '{email_str}' registrado en Industrias Beta.")

        # Catálogo empresa B (1 categoría + artículos de ACTIVOS_EMPRESA_B)
        stmt_cat_b = select(ArticleCategoryModel).where(ArticleCategoryModel.empresa_id == company_b.id.value)
        res_cat_b = await uow.session.execute(stmt_cat_b)
        cat_b = res_cat_b.scalars().first()
        if not cat_b:
            cat_b = ArticleCategoryModel(
                id=uuid.uuid4(), empresa_id=company_b.id.value,
                nombre="Equipos Generales", descripcion="Equipos varios",
            )
            uow.session.add(cat_b)
            await uow.session.flush()

        for act_def in ACTIVOS_EMPRESA_B:
            stmt_art = select(CatalogArticleModel).where(
                CatalogArticleModel.empresa_id == company_b.id.value,
                CatalogArticleModel.name == act_def["articulo_nombre"],
            )
            art_model = (await uow.session.execute(stmt_art)).scalar_one_or_none()
            if not art_model:
                art_model = CatalogArticleModel(
                    id=uuid.uuid4(), category_id=cat_b.id, empresa_id=company_b.id.value,
                    name=act_def["articulo_nombre"], description="",
                    manufacturer="", model="", unit_of_measure="unidad",
                )
                uow.session.add(art_model)
                await uow.session.flush()

        # Activos empresa B
        existing_assets_b, _ = await uow.assets.list_by_company(company_b.id, offset=0, limit=100)
        if not existing_assets_b:
            for act_def in ACTIVOS_EMPRESA_B:
                stmt_art = select(CatalogArticleModel).where(
                    CatalogArticleModel.empresa_id == company_b.id.value,
                    CatalogArticleModel.name == act_def["articulo_nombre"],
                )
                art_model = (await uow.session.execute(stmt_art)).scalar_one_or_none()
                if not art_model:
                    continue
                # Ubicación por defecto: sede simple
                existing_locs_b = await uow.locations.get_tree(company_b.id)
                if not existing_locs_b:
                    sede = Location.create(
                        empresa_id=company_b.id, parent_id=None,
                        nombre="Sede Industrias Beta", tipo=LocationType.HEADQUARTERS,
                        parent_type=None, descripcion="Sede principal",
                    )
                    await uow.locations.save(sede)
                    await uow.session.flush()
                    ubicacion_b = sede
                else:
                    ubicacion_b = existing_locs_b[0]

                asset = Asset.create(
                    empresa_id=company_b.id,
                    articulo_id=art_model.id,
                    ubicacion_id=ubicacion_b.id,
                    serial_interno=act_def["serial"],
                    codigo_activo=act_def["codigo"],
                    estado=act_def["estado"],
                    fecha_adquisicion=act_def["fecha"],
                    valor_monetario=act_def["valor"],
                    moneda="USD",
                )
                await uow.assets.save(asset)
                await uow.session.flush()
            print(f"✅ {len(ACTIVOS_EMPRESA_B)} activos creados en Industrias Beta.")

        await uow.commit()
