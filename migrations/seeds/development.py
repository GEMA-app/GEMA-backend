# migrations/seeds/development.py
"""Seed de desarrollo: empresa demo con 6 usuarios, 6 roles, ubicaciones, catálogo y activos."""

import uuid
from datetime import date
from decimal import Decimal

from app.domain.entities import Asset, Company, Location, Permission, Role, User, UserPreference
from app.domain.enums import AssetStatus, CompanyStatus, LocationType, PermissionModule, Theme
from app.domain.value_objects import CompanyId, Email, HashedPassword, Slug
from app.infrastructure.db.models import ArticleCategoryModel, CatalogArticleModel
from app.infrastructure.db.models.company import SubscriptionPlanModel
from app.infrastructure.events.bus import InProcessEventBus
from app.infrastructure.security.hashing import BcryptPasswordHasher
from app.infrastructure.uow import SqlAlchemyUnitOfWork

# ─── CONFIGURACIÓN DE ROLES ───────────────────────────────────

ROLES_CONFIG = {
    "Administrador": {
        "desc": "Acceso completo a todos los módulos del sistema",
        "permisos": {
            PermissionModule.ASSETS: (True, True, True, True),
            PermissionModule.MAINTENANCE: (True, True, True, True),
            PermissionModule.INVENTORY: (True, True, True, True),
            PermissionModule.REPORTS: (True, True, True, True),
            PermissionModule.ADMIN: (True, True, True, True),
            PermissionModule.PREFERENCES: (True, False, True, False),  # Solo view + edit
            PermissionModule.SYSTEM_AUDIT: (True, True, True, True),
        },
    },
    "Supervisor de Activos": {
        "desc": "Gestiona activos y supervisa su ciclo de vida",
        "permisos": {
            PermissionModule.ASSETS: (True, True, True, True),
            PermissionModule.MAINTENANCE: (True, False, False, False),
            PermissionModule.INVENTORY: (True, False, False, False),
            PermissionModule.REPORTS: (True, False, False, False),
            PermissionModule.ADMIN: (True, False, False, False),
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
            PermissionModule.MAINTENANCE: (True, False, False, False),
            PermissionModule.INVENTORY: (True, True, True, True),
            PermissionModule.REPORTS: (True, False, False, False),
            PermissionModule.ADMIN: (True, False, False, False),
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
    ("admin@demo.com",       "Carlos Méndez",    "Administrador"),
    ("supervisor@demo.com",  "María González",   "Supervisor de Activos"),
    ("tecnico@demo.com",     "Pedro Hernández",  "Técnico de Mantenimiento"),
    ("almacen@demo.com",     "Ana Rodríguez",    "Almacenista"),
    ("operaciones@demo.com", "Luis Martínez",    "Supervisor de Operaciones"),
    ("consulta@demo.com",    "Sofía López",      "Consultor (Solo Lectura)"),
]

# ─── SEED PRINCIPAL ───────────────────────────────────────────

async def seed() -> None:
    """Pobla la base de datos de desarrollo con datos iniciales."""
    uow = SqlAlchemyUnitOfWork(event_bus=InProcessEventBus())
    hasher = BcryptPasswordHasher()
    password_hash = hasher.hash("Password123!")

    async with uow:
        # 1. Crear Plan de Suscripción (directamente vía modelo ORM ya que no hay puerto)
        from sqlalchemy import select
        stmt_plan = select(SubscriptionPlanModel).where(
            SubscriptionPlanModel.nombre == "Plan Premium GEMA"
        )
        res_plan = await uow.session.execute(stmt_plan)
        plan = res_plan.scalar_one_or_none()
        if not plan:
            plan = SubscriptionPlanModel(
                id=uuid.UUID("d6346dd5-b62a-4aed-bfdb-a9ab1ff8a8b1"),
                nombre="Plan Premium GEMA",
                descripcion=(
                    "Plan premium con todas las características de la plataforma habilitadas"
                ),
                max_activos=100,
                max_usuarios=20,
                precio_mensual_usd=Decimal("99.99")
            )
            uow.session.add(plan)
            await uow.session.flush()
            print("✅ Plan Premium GEMA creado.")

        # 2. Crear Empresa (Tenant)
        existing_company = await uow.companies.get_by_slug(Slug.from_name("ACME S.A."))
        if existing_company:
            print("ℹ️ Empresa 'ACME S.A.' ya existe. Saltando creación.")
            company = existing_company
        else:
            # Fijamos el UUID de la empresa para reproducibilidad
            fixed_company_id = CompanyId(uuid.UUID("8719bfd0-5cfb-4a5d-9f2b-da9ab1ff8a8b"))
            company = Company(
                id=fixed_company_id,
                nombre="ACME S.A.",
                slug=Slug.from_name("ACME S.A."),
                rif="J-12345678-9",
                email_contacto="admin@demo.com",
                estado=CompanyStatus.ACTIVE,
                plan_id=plan.id,
            )
            await uow.companies.save(company)
            await uow.session.flush()
            print("✅ Empresa 'ACME S.A.' creada.")

        # 3. Crear Roles
        existing_roles = await uow.roles.list_by_company(company.id)
        roles_map = {r.nombre: r for r in existing_roles}

        for nombre, config in ROLES_CONFIG.items():
            permisos_dict = config["permisos"]
            assert isinstance(permisos_dict, dict)
            permisos = [
                Permission(
                    module=mod,
                    can_view=v, can_create=c, can_edit=e, can_delete=d,
                )
                for mod, (v, c, e, d) in permisos_dict.items()
            ]
            desc = config["desc"]
            assert isinstance(desc, str)

            if nombre in roles_map:
                print(f"ℹ️ Rol '{nombre}' ya existe. Sincronizando permisos.")
                rol = roles_map[nombre]
                rol.permisos = permisos
                await uow.roles.save(rol)
                continue

            rol = Role.create(
                empresa_id=company.id,
                nombre=nombre,
                descripcion=desc,
                permisos=permisos,
            )
            await uow.roles.save(rol)
            roles_map[nombre] = rol
            print(f"✅ Rol '{nombre}' creado.")

        # 4. Crear Usuarios, Preferencias y Asignar Roles
        for email_str, nombre, rol_nombre in PERSONAL:
            email = Email(email_str)
            existing_user = await uow.users.get_by_email(email)
            if existing_user:
                print(f"ℹ️ Usuario '{email_str}' ya existe. Saltando creación.")
                continue

            user = User.register(
                email=email,
                password_hash=HashedPassword(password_hash),
                empresa_id=company.id,
                nombre=nombre,
            )
            await uow.users.save(user)
            await uow.session.flush()

            rol = roles_map[rol_nombre]
            rol.record_assignment(user.id)
            await uow.roles.save(rol)
            await uow.roles.assign_to_user(rol.id, user.id)

            pref = UserPreference.create(
                usuario_id=user.id, empresa_id=company.id, tema=Theme.SYSTEM
            )
            await uow.preferences.save(pref)
            print(f"✅ Usuario '{email_str}' registrado con preferencias y rol '{rol_nombre}'.")

        # 5. Crear Estructura de Ubicaciones
        # Sede -> Planta -> Area -> Section
        # Verificar si existe sede
        existing_locs = await uow.locations.get_tree(company.id)
        if existing_locs:
            print("ℹ️ Estructura de ubicaciones ya existe. Saltando creación.")
            sede = next(loc for loc in existing_locs if loc.tipo == LocationType.HEADQUARTERS)
            planta = next(loc for loc in existing_locs if loc.tipo == LocationType.PLANT)
            area = next(loc for loc in existing_locs if loc.tipo == LocationType.AREA)
            seccion = next(loc for loc in existing_locs if loc.tipo == LocationType.SECTION)
        else:
            sede = Location.create(
                empresa_id=company.id,
                parent_id=None,
                nombre="Sede Principal GEMA",
                tipo=LocationType.HEADQUARTERS,
                parent_type=None,
                descripcion="Sede corporativa y operativa principal"
            )
            await uow.locations.save(sede)
            await uow.session.flush()

            planta = Location.create(
                empresa_id=company.id,
                parent_id=sede.id,
                nombre="Planta de Producción A",
                tipo=LocationType.PLANT,
                parent_type=LocationType.HEADQUARTERS,
                descripcion="Línea de montaje y empaque"
            )
            await uow.locations.save(planta)
            await uow.session.flush()

            area = Location.create(
                empresa_id=company.id,
                parent_id=planta.id,
                nombre="Área de Compresores",
                tipo=LocationType.AREA,
                parent_type=LocationType.PLANT,
                descripcion="Sistema neumático central"
            )
            await uow.locations.save(area)
            await uow.session.flush()

            seccion = Location.create(
                empresa_id=company.id,
                parent_id=area.id,
                nombre="Línea de Control de Válvulas",
                tipo=LocationType.SECTION,
                parent_type=LocationType.AREA,
                descripcion="Sub-sistema de regulación de presión"
            )
            await uow.locations.save(seccion)
            await uow.session.flush()
            print("✅ Estructura jerárquica de ubicaciones creada.")

        # 6. Crear Categorías de Artículos y Artículos de Catálogo
        stmt_cat = select(ArticleCategoryModel).where(
            ArticleCategoryModel.empresa_id == company.id.value
        )
        res_cat = await uow.session.execute(stmt_cat)
        cat_model = res_cat.scalars().first()
        if cat_model:
            print("ℹ️ Categorías y artículos ya existen en el catálogo. Saltando creación.")
            existing_article = (await uow.session.execute(
                select(CatalogArticleModel).where(
                    CatalogArticleModel.empresa_id == company.id.value
                )
            )).scalars().first()
            assert existing_article is not None
            articulo_id = existing_article.id
        else:
            cat_id = uuid.uuid4()
            cat_model = ArticleCategoryModel(
                id=cat_id,
                empresa_id=company.id.value,
                nombre="Equipos Rotativos",
                descripcion="Motores, bombas, turbinas y maquinaria rotativa"
            )
            uow.session.add(cat_model)
            await uow.session.flush()

            articulo_id = uuid.uuid4()
            art_model = CatalogArticleModel(
                id=articulo_id,
                categoria_id=cat_id,
                empresa_id=company.id.value,
                nombre="Motor Eléctrico trifásico 5HP",
                descripcion="Motor eléctrico WEG W22 Premium IP55",
                fabricante="WEG",
                modelo="W22 5HP",
                unidad_medida="unidad"
            )
            uow.session.add(art_model)
            await uow.session.flush()
            print("✅ Categorías y artículos agregados al catálogo.")

        # 7. Crear Activo
        # Buscar si hay activos creados
        existing_assets, _ = await uow.assets.list_by_company(company.id, offset=0, limit=10)
        if existing_assets:
            print("ℹ️ Activo demo ya existe. Saltando creación.")
        else:
            asset = Asset.create(
                empresa_id=company.id,
                articulo_id=articulo_id,
                ubicacion_id=seccion.id,
                serial_interno="SN-WEG-5HP-001",
                codigo_activo="ACT-MOT-001",
                estado=AssetStatus.OPERATIONAL,
                fecha_adquisicion=date(2026, 1, 15),
                valor_monetario=Decimal("450.00"),
                moneda="USD"
            )
            await uow.assets.save(asset)
            await uow.session.flush()
            print("✅ Activo demo 'ACT-MOT-001' creado en Sección de Válvulas.")

        await uow.commit()
