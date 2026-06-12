# AGENTS.md — GEMA Backend

> Documento de contexto para agentes de IA que trabajen con este repositorio.

---

## Identidad del Proyecto

- **Nombre**: GEMA Backend
- **Descripción**: API REST backend para el sistema GEMA de UNEGIA, construido con arquitectura hexagonal (Ports & Adapters) y Domain-Driven Design táctico.
- **Lenguaje**: Python 3.12+
- **Framework**: FastAPI con Uvicorn (desarrollo) y Gunicorn (producción)
- **Gestor de dependencias**: Poetry
- **Base de datos**: PostgreSQL 16 (driver asíncrono: `asyncpg`)
- **ORM**: SQLAlchemy 2.0 (modo async)
- **Migraciones**: Alembic (async)
- **Caché / Blocklist**: Redis 7 (driver asíncrono: `redis.asyncio`)
- **Autenticación**: JWT (PyJWT) con access/refresh tokens y blocklist en Redis
- **Hashing**: bcrypt
- **Logging**: structlog (JSON en producción, consola en desarrollo)
- **Serialización API**: JSON:API (spec compliant con `application/vnd.api+json`)
- **Validación/Configuración**: Pydantic v2 + pydantic-settings

---

## Arquitectura

### Estilo Arquitectónico

Arquitectura Hexagonal (Ports & Adapters) con separación estricta en 5 capas:

```
Domain → Application → Infrastructure → Presentation
  ↑
Composition
```

La dependencia siempre fluye hacia adentro: las capas externas dependen de las internas, nunca al revés. La capa de Application define **Ports** (interfaces `Protocol`) que Infrastructure implementa.

### Capas

| Capa | Directorio | Responsabilidad |
|------|-----------|-----------------|
| **Domain** | `src/app/domain/` | Entidades, Value Objects, Enums, Eventos de Dominio, Excepciones |
| **Application** | `src/app/application/` | Casos de Uso, DTOs, Ports (interfaces), Servicios de aplicación |
| **Infrastructure** | `src/app/infrastructure/` | Implementaciones: DB, Cache, Repositorios, Security/RBAC, Config |
| **Presentation** | `src/app/presentation/` | Endpoints FastAPI, Schemas JSON:API, Middlewares, Exception Handlers |
| **Composition** | `src/app/composition/` | Composition Root (inyección de dependencias con `Depends`) |

### Modelo SaaS y Multi-Tenancy

GEMA es una plataforma SaaS multi-tenant que implementa aislamiento a nivel de base de datos usando discriminación por columna.
- **Tenant**: Cada empresa registrada representa un tenant único con su `empresa_id` (UUID).
- **Aislamiento**: Los modelos ORM multi-tenant heredan de `TenantMixin` el cual añade automáticamente la clave foránea `empresa_id` con índice a nivel de base de datos.
- **Flujo de Onboarding SaaS**: Al registrar un nuevo usuario mediante `/v1/auth/registrar`, el sistema:
  1. Crea automáticamente una nueva empresa (`Company`).
  2. Crea el usuario (`User`) vinculado a dicha empresa (`empresa_id`).
  3. Genera un rol con nombre "Administrador" que contiene todos los permisos del sistema.
  4. Asigna ese rol de administrador al usuario creado.
  5. Emite los tokens JWT iniciales.

### Sistema RBAC (Role-Based Access Control)

La autorización se basa en roles y permisos específicos asignados a nivel de tenant:
- **Roles**: Entidad `Role` definida por empresa (`empresa_id`) con su lista de permisos granularizados.
- **Permisos**: Value Object `Permission` que define permisos granulares por módulo y acciones CRUD:
  - **Módulos (`PermissionModule`)**: `assets` (Activos), `maintenance` (Mantenimiento), `inventory` (Inventario), `reports` (Reportes), `admin` (Administración del sistema), `preferences` (Preferencias).
  - **Acciones**: `view` (Visualizar), `create` (Crear), `edit` (Editar), `delete` (Eliminar).
- **Decorador de Seguridad**: Los endpoints REST validan permisos en tiempo de ejecución usando la dependencia `Depends(require_permission(modulo, accion, company_id))`. La función `require_permission()` ahora incluye validación de tenant: verifica que el `company_id` del path coincida con la empresa del token JWT, además del permiso RBAC.

### Flujo de una Request

```
Request HTTP

  → Middlewares (RequestId → ContentType → Accept → RateLimit)
  → Router FastAPI (v1)
  → Endpoint (FastAPI valida Token + Tenant + Permiso RBAC por dependencia require_permission())
  → Composition Root (resuelve dependencias en el paquete composition/container)
  → Use Case (orquesta la lógica de negocio y abre transacción vía UoW)
  → Domain Entity (ejecuta reglas de negocio, valida invariantes y genera eventos)
  → Repository Port (interfaz) → Repository Adapter (query SQL en base de datos)
  → Unit Of Work Commit (guarda los cambios en base de datos de manera atómica)
  → Response JSON:API
```

### Flujo de Eventos de Dominio

El sistema implementa un despacho síncrono de eventos de dominio recolectados por el Unit of Work:
1. **Generación**: Las entidades de dominio acumulan eventos internamente al ejecutar acciones (ej: `role.record_assignment()`).
2. **Recolección**: Al persistir una entidad a través de un repositorio (`repo.save(entity)`), este extrae los eventos acumulados si la entidad cumple con el protocolo `EventProducer`, y los almacena en una lista interna del Unit of Work (`_pending_events`).
3. **Publicación**: Al confirmar la transacción (`uow.commit()`), si el commit en base de datos es exitoso, los eventos pendientes se publican en memoria a través del `EventBusPort`.

---


## Estructura de Directorios

```
├── src/app/
│   ├── main.py                          # Entry point, lifespan, registro de middlewares y routers
│   ├── domain/
│   │   ├── enums.py                     # CompanyStatus, PermissionModule, AssetStatus, LocationType
│   │   ├── events.py                    # DomainEvents (UserRegistered, CompanyCreated, RoleAssigned, etc.)
│   │   ├── entities/                    # Paquete modular de entidades
│   │   │   ├── __init__.py              # Exporta User, Company, Role, Permission, Asset, Location
│   │   │   ├── user.py                  # Entidad User con empresa_id, nombre, teléfono y roles asignados
│   │   │   ├── preference.py           # Entidad UserPreference (método change_theme(), themes, pk)
│   │   │   ├── company.py               # Entidad Company
│   │   │   ├── role.py                  # Entidad Role
│   │   │   ├── permission.py            # Entidad Permission (Value Object)
│   │   │   ├── asset.py                 # Entidad Asset (Activos físicos)
│   │   │   └── location.py              # Entidad Location (Ubicaciones físicas jerárquicas)
│   │   ├── exceptions/                  # Paquete modular de excepciones del dominio
│   │   │   ├── __init__.py              # Re-exporta todas las excepciones para retrocompatibilidad
│   │   │   ├── base.py                  # Clase base DomainException
│   │   │   └── auth.py, company.py, role.py, permission.py, asset.py, location.py, preference.py
│   │   └── value_objects/               # Paquete modular de objetos de valor
│   │       ├── __init__.py              # Re-exporta todos los value objects
│   │       ├── credential.py           # Email, PlainPassword, HashedPassword
│   │       ├── identifier.py           # UserId, CompanyId, RoleId, AssetId, LocationId
│   │       └── slug.py                  # Slug URL-friendly para empresas
│   ├── application/
│   │   ├── dtos/                        # Paquete modular de DTOs
│   │   │   ├── auth_dtos.py
│   │   │   ├── company_dtos.py
│   │   │   ├── role_dtos.py
│   │   │   ├── asset_dtos.py
│   │   │   ├── location_dtos.py
│   │   │   └── preference_dtos.py
│   │   ├── ports/
│   │   │   ├── auth.py                  # PasswordHasherPort, TokenServicePort
│   │   │   ├── company_repository.py
│   │   │   ├── role_repository.py
│   │   │   ├── asset_repository.py
│   │   │   ├── location_repository.py
│   │   │   ├── preference_repository.py # PreferenceRepositoryPort (interfaz con pk_column)
│   │   │   ├── repository.py            # UserRepositoryPort
│   │   │   └── unit_of_work.py          # UnitOfWorkPort
│   │   ├── services/
│   │   │   └── authorization_service.py # Interfaz del servicio de autorización RBAC
│   │   └── use_cases/
│   │       ├── auth/                    # Paquete modular de casos de uso de autenticación
│   │       │   ├── __init__.py          # Re-exporta los casos de uso de auth
│   │       │   ├── login_user.py
│   │       │   ├── logout_user.py
│   │       │   ├── refresh_token.py
│   │       │   ├── register_user.py
│   │       │   └── get_current_user.py
│   │       ├── company/                 # CRUD de empresas
│   │       ├── role/                    # CRUD de roles, assign/revoke a usuario
│   │       ├── asset/                   # CRUD de activos
│   │       ├── preferences/             # CRUD de preferencias de usuario
│   │       └── location/                # CRUD de ubicaciones y reconstrucción de árbol jerárquico
│   ├── infrastructure/
│   │   ├── config/
│   │   │   ├── settings.py              # Pydantic Settings
│   │   │   └── logger.py               # structlog setup
│   │   ├── db/
│   │   │   ├── base.py                  # DeclarativeBase de SQLAlchemy
│   │   │   ├── session.py              # AsyncEngine + async_sessionmaker
│   │   │   └── models/                  # Paquete modular de modelos ORM
│   │   │       ├── __init__.py          # Exporta todos los modelos ORM
│   │   │       ├── mixins.py            # TenantMixin y TimestampMixin
│   │   │       ├── user.py              # UserModel
│   │   │       ├── company.py           # CompanyModel y SubscriptionPlanModel
│   │   │       ├── role.py              # RoleModel, PermissionModel, RoleUserModel
│   │   │       ├── asset.py             # AssetModel
│   │   │       ├── location.py          # LocationModel (autocontrol de jerarquía)
│   │   │       ├── preference.py       # UserPreferenceModel (modelo ORM de preferencias)
│   │   │       └── catalog.py           # Modelos de catálogo (placeholder)
│   │   ├── repositories/                # Adapters concretos de persistencia
│   │   │   ├── base.py                  # SqlAlchemyRepository genérico con pk_column como atributo de clase
│   │   │   ├── user_repository.py
│   │   │   ├── company_repository.py
│   │   │   ├── role_repository.py
│   │   │   ├── asset_repository.py
│   │   │   ├── location_repository.py
│   │   │   └── preference_repository.py # SqlAlchemyPreferenceRepository (pk_column = "usuario_id")
│   │   ├── security/
│   │   │   ├── hashing.py              # BcryptPasswordHasher
│   │   │   ├── jwt.py                  # PyJwtTokenService
│   │   │   └── authorization.py        # RbacAuthorizationService (adapter)
│   │   ├── cache/
│   │   │   └── redis.py                # Cliente global async Redis
│   │   └── uow.py                      # SqlAlchemyUnitOfWork
│   ├── presentation/
│   │   ├── exception_handlers/          # Paquete modular de manejadores de excepciones
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # Respuesta jsonapi_response estándar
│   │   │   ├── domain.py                # Mapeo declarativo de excepciones de dominio a HTTP
│   │   │   ├── http.py                  # Manejador de Starlette HTTPExceptions
│   │   │   └── validation.py            # Manejador de RequestValidationErrors (Pydantic)
│   │   ├── middlewares/
│   │   │   ├── request_id.py            # Correlation ID
│   │   │   ├── content_type.py          # Validación Content-Type JSON:API
│   │   │   ├── accept.py               # Validación Accept header
│   │   │   └── rate_limit.py           # Rate limiting
│   │   └── api/
│   │       └── v1/
│   │           ├── router.py            # v1_router con endpoints registrados
│   │           ├── endpoints/
│   │           │   ├── auth.py          # /v1/auth/ (registrar, ingresar, refrescar, cerrar-sesion, yo)
│   │           │   ├── companies.py     # /v1/empresas
│   │           │   ├── roles.py         # /v1/empresas/{empresa_id}/roles
│   │           │   ├── assets.py        # /v1/empresas/{empresa_id}/activos
│   │           │   ├── locations.py     # /v1/empresas/{empresa_id}/ubicaciones
│   │           │   └── preferences.py   # /v1/empresas/{empresa_id}/yo/preferencias (protegido con require_permission)
│   │           └── schemas/             # Schemas de validación y representación JSON:API
│   │               ├── jsonapi_base.py
│   │               ├── auth.py
│   │               ├── company.py
│   │               ├── role.py
│   │               ├── asset.py
│   │               ├── location.py
│   │               └── preferences.py
│   └── composition/
│       └── container/                   # Paquete modular de inyección de dependencias
│           ├── __init__.py              # Re-exporta todas las fábricas
│           ├── common.py                # Dependencias compartidas (UoW, Hasher, TokenService, AuthService)
│           └── auth.py, company.py, role.py, asset.py, location.py (Fábricas específicas de dominio)
```

---

## Convenciones de Código

### Estilo y Formateo

- **Linter**: Ruff (reglas: E, W, F, I, UP, B, SIM, D)
- **Formatter**: Black (line-length: 100)
- **Type Checker**: MyPy (modo strict)
- **Docstrings**: Google convention (en español)
- **Line length**: 100 caracteres

### Idioma

- **Código fuente**: identificadores en inglés (`User`, `register`, `get_by_email`)
- **Rutas de la API REST**: en español (ej: `/v1/auth/registrar`, `/v1/empresas/{empresa_id}/activos`)
- **Docstrings y comentarios**: en español
- **Mensajes de error de dominio**: en español
- **Nombres de archivos**: snake_case en inglés

### Convenciones de Excepciones de Dominio y Mapeo HTTP

| Excepción de Dominio | Código HTTP | Mensaje/Descripción |
|----------------------|-------------|---------------------|
| `WeakPasswordError` | 422 | Contraseña débil |
| `InvalidEmailError` | 422 | Formato de correo electrónico inválido |
| `UserAlreadyExistsError` | 409 | El correo ya está registrado en el sistema |
| `InvalidCredentialsError` | 401 | Credenciales de acceso incorrectas |
| `UserInactiveError` | 403 | El usuario está suspendido o inactivo |
| `InvalidTokenError` | 401 | Token JWT inválido, expirado o en lista negra |
| `CompanyNotFoundError` | 404 | Empresa no encontrada en la base de datos |
| `CompanySlugExistsError` | 409 | El slug identificador de empresa ya existe |
| `RoleNotFoundError` | 404 | El rol solicitado no existe en la empresa |
| `RoleNameExistsError` | 409 | Ya existe un rol con ese nombre en la empresa |
| `InsufficientPermissionsError` | 403 | Permisos de RBAC insuficientes para la acción |
| `AssetNotFoundError` | 404 | Activo físico no encontrado |
| `AssetCodeExistsError` | 409 | Código de activo ya registrado en el tenant |
| `AssetSerialExistsError` | 409 | Número de serie de activo ya registrado en el tenant |
| `LocationNotFoundError` | 404 | Ubicación no encontrada |
| `LocationCircularReferenceError` | 422 | Error en la jerarquía (referencia circular) |
| `LocationInvalidTypeHierarchyError`| 422 | Tipo de ubicación inconsistente con su padre |
| `PreferenceNotFoundError` | 404 | Preferencias de usuario no encontradas |
| `PreferenceThemeInvalidError` | 422 | El tema visual especificado no es válido |
| `AssetInvalidTransitionError` | 422 | Transición de estado no permitida |
| `EmptySerialError` | 422 | Número de serie vacío |
| `EmptyAssetCodeError` | 422 | Código de activo vacío |
| `CompanyAlreadyCancelledError` | 422 | Empresa ya cancelada |
| `CompanyNotSuspendedError` | 422 | Empresa no está suspendida |
| `EmptyLocationNameError` | 422 | Nombre de ubicación vacío |

---

## API Endpoints Disponibles

| Método | Ruta | Descripción | Auth | Permiso RBAC |
|--------|------|-------------|------|--------------|
| `POST` | `/v1/auth/registrar` | Registro de usuario (Onboarding SaaS) | No | - |
| `POST` | `/v1/auth/ingresar` | Inicio de sesión | No | - |
| `POST` | `/v1/auth/refrescar` | Rotación de tokens | No | - |
| `POST` | `/v1/auth/cerrar-sesion` | Cierre de sesión | Bearer | - |
| `GET` | `/v1/auth/yo` | Perfil del usuario actual | Bearer | - |
| `POST` | `/v1/empresas` | Crear una nueva empresa | Bearer | `admin:create` |
| `GET` | `/v1/empresas` | Listar empresas | Bearer | - |
| `GET` | `/v1/empresas/{empresa_id}` | Obtener una empresa | Bearer | - |
| `PATCH` | `/v1/empresas/{empresa_id}` | Actualizar datos de empresa | Bearer | `admin:edit` |
| `DELETE` | `/v1/empresas/{empresa_id}` | Eliminar empresa | Bearer | `admin:delete` |
| `POST` | `/v1/empresas/{empresa_id}/roles` | Crear nuevo rol | Bearer | `admin:create` |
| `GET` | `/v1/empresas/{empresa_id}/roles` | Listar todos los roles | Bearer | - |
| `GET` | `/v1/empresas/{empresa_id}/roles/{rol_id}` | Obtener detalles de un rol | Bearer | - |
| `PATCH` | `/v1/empresas/{empresa_id}/roles/{rol_id}`| Actualizar rol y permisos | Bearer | `admin:edit` |
| `DELETE` | `/v1/empresas/{empresa_id}/roles/{rol_id}`| Eliminar un rol | Bearer | `admin:delete` |
| `POST` | `/v1/empresas/{empresa_id}/roles/{rol_id}/asignar`| Asignar rol a usuario | Bearer | `admin:edit` |
| `DELETE`| `/v1/empresas/{empresa_id}/roles/{rol_id}/revocar`| Revocar rol a usuario (query: `usuario_id`)| Bearer | `admin:edit` |
| `POST` | `/v1/empresas/{empresa_id}/activos` | Crear un activo físico | Bearer | `assets:create` |
| `GET` | `/v1/empresas/{empresa_id}/activos` | Listar activos (filtros: `estado`, `ubicacion_id`)| Bearer | `assets:view` |
| `GET` | `/v1/empresas/{empresa_id}/activos/{activo_id}` | Obtener detalles de un activo | Bearer | `assets:view` |
| `PATCH` | `/v1/empresas/{empresa_id}/activos/{activo_id}` | Actualizar datos de activo | Bearer | `assets:edit` |
| `DELETE` | `/v1/empresas/{empresa_id}/activos/{activo_id}` | Eliminar activo | Bearer | `assets:delete` |
| `POST` | `/v1/empresas/{empresa_id}/ubicaciones` | Crear ubicación jerárquica | Bearer | `admin:create` |
| `GET` | `/v1/empresas/{empresa_id}/ubicaciones` | Obtener árbol de ubicaciones completo | Bearer | - |
| `GET` | `/v1/empresas/{empresa_id}/ubicaciones/{ubicacion_id}`| Obtener detalles de ubicación | Bearer | - |
| `PATCH` | `/v1/empresas/{empresa_id}/ubicaciones/{ubicacion_id}`| Actualizar ubicación | Bearer | `admin:edit` |
| `DELETE` | `/v1/empresas/{empresa_id}/ubicaciones/{ubicacion_id}`| Eliminar ubicación | Bearer | `admin:delete` |
| `GET` | `/v1/empresas/{empresa_id}/ubicaciones/{ubicacion_id}/hijos`| Listar ubicaciones hijas directas | Bearer | - |
| `GET` | `/v1/empresas/{empresa_id}/yo/preferencias` | Obtener preferencias del usuario actual | Bearer | `preferencias:view` |
| `PATCH` | `/v1/empresas/{empresa_id}/yo/preferencias` | Actualizar preferencias del usuario actual | Bearer | `preferencias:edit` |
| `GET` | `/salud/activo` | Liveness probe | No | - |
| `GET` | `/salud/listo` | Readiness probe (DB + Redis) | No | - |

### Convención de Seguridad

#### 1. Validación de Tenant (UUID Normalization)

Todos los endpoints que reciben `empresa_id` en el path DEBEN normalizar el UUID antes de compararlo con el tenant del usuario autenticado. Esto previene bypass por diferencias de formato (con/sin guiones, mayúsculas/minúsculas).

```python
# CORRECTO: Normalización vía UUID()
if UUID(empresa_id) != UUID(user_empresa_id):
    raise InsufficientPermissionsError("No tienes acceso a esta empresa")
```

La función `validate_tenant_access()` en `dependencies.py` implementa esta normalización y se usa en:

- `require_tenant_read()` — endpoints GET que solo necesitan validación de tenant (sin RBAC)
- `require_permission()` — endpoints que necesitan tenant + RBAC

#### 2. Tres Patrones de Dependencia

| Patrón | Función | Cuándo usarlo |
|--------|---------|---------------|
| **Platform** | `require_platform_permission(module, action)` | Endpoints SIN `empresa_id` en el path (ej: `POST /v1/empresas`) |
| **Tenant + RBAC** | `require_permission(module, action)` | Endpoints CON `empresa_id` en el path que requieren permiso específico |
| **Solo Tenant** | `require_tenant_read` | Endpoints GET que solo necesitan verificar acceso al tenant (sin RBAC) |

#### 3. Nomenclatura de Parámetros de Path

Todos los parámetros de ID en los paths DEBEN usar el nombre específico de la entidad:

| Endpoint | Incorrecto | Correcto |
|----------|-----------|----------|
| `/empresas/{id}` | `{id}` | `{empresa_id}` |
| `/roles/{id}` | `{id}` | `{rol_id}` |
| `/activos/{id}` | `{id}` | `{activo_id}` |
| `/ubicaciones/{id}` | `{id}` | `{ubicacion_id}` |
| `/ubicaciones/{id}/hijos` | `{id}` | `{ubicacion_id}` |

Esto elimina ambigüedad y previene errores de tipo IDOR.

#### 4. Mapeo de IntegrityError a 409 Conflict

Las violaciones de unicidad en PostgreSQL se capturan en `integrity_error_handler` (Presentation) y se mapean a excepciones de dominio con HTTP 409 Conflict. El handler usa doble mecanismo de parsing:

1. `__cause__.constraint_name` — asyncpg expone el nombre directamente
2. `str(exc.orig)` — fallback para todos los drivers

#### 5. Type Hints Correctos

- `require_permission()` retorna `UserResponse`, no `Any`
- `get_current_active_user()` retorna `UserResponse`, no `Any`
- `require_tenant_read()` retorna `UserResponse`, no `Any`

#### 6. Endpoints GET sin RBAC pero con Tenant Check

Los siguientes endpoints GET usan `require_tenant_read` en lugar de `require_permission` porque no requieren un permiso RBAC específico, pero SÍ necesitan validar que el usuario pertenece al tenant:

- `GET /v1/empresas/{empresa_id}`
- `GET /v1/empresas/{empresa_id}/ubicaciones`
- `GET /v1/empresas/{empresa_id}/ubicaciones/{ubicacion_id}`
- `GET /v1/empresas/{empresa_id}/ubicaciones/{ubicacion_id}/hijos`
- `GET /v1/empresas/{empresa_id}/roles`
- `GET /v1/empresas/{empresa_id}/roles/{rol_id}`


---

## Estructura de Migraciones y Semillas (Seeds)

### 1. Separación de Migraciones (DDL) y Semillas (DML)
- **Migraciones (Esquema/DDL):** Ubicadas en `migrations/versions/`. Son inmutables una vez aplicadas en producción. Deben formar una cadena estrictamente lineal.
  - *Regla Crítica:* Para que `alembic revision --autogenerate` detecte todos los modelos, `migrations/env.py` debe importar todos los modelos ORM (o el paquete `models` que los registra en `Base.metadata`).
- **Semillas (Datos/DML):** Ubicadas en `migrations/seeds/`. Son archivos de datos de prueba volátiles y deben diseñarse para ser idempotentes (poder ejecutarse varias veces sin duplicar registros).

### 2. Estructura de Semillas de Personal y Roles
Para la inicialización del sistema en desarrollo y staging, se define una estructura estándar con **6 roles** granularizados por módulo en la empresa de pruebas:
- **Administrador:** Acceso completo (puede_ver/crear/editar/eliminar) en todos los módulos.
- **Supervisor de Activos:** CRUD en Activos, solo lectura en el resto (excepto Admin).
- **Técnico de Mantenimiento:** CRUD en Mantenimiento, lectura en Activos e Inventario, creación en Reportes.
- **Almacenista:** CRUD en Inventario, lectura en Activos y Reportes.
- **Supervisor de Operaciones:** CRUD en Reportes, Mantenimiento e Inventario, lectura en Administración.
- **Consultor:** Solo lectura en todos los módulos.

El runner CLI en `migrations/seeds/runner.py` se ejecuta dentro del contenedor de la aplicación:
```bash
docker compose exec app python -m migrations.seeds.runner [dev|staging|test]
```

---

## Componentes Diferidos (Pendientes de futuros Sprints)

Para mantener el alcance de entrega acotado y enfocado en el núcleo de negocio del Sprint II, los siguientes componentes han sido **diferidos y marcados explícitamente como pendientes**:

1. **Gestión de Planes de Suscripción (`planes_suscripcion`)**:
   - *Estado actual*: Se crea la estructura de tablas y el modelo ORM `SubscriptionPlanModel` junto con seeds estáticos en la migración de base de datos.
   - *Pendiente*: El desarrollo de endpoints REST, lógica de negocios CRUD para planes y la pasarela de cobros asociada.

2. **CRUD Completo de Catálogo de Artículos (`categorias_articulos` y `articulos_catalogo`)**:
   - *Estado actual*: Se crearon las tablas correspondientes y modelos ORM placeholders mínimos (`ArticleCategoryModel`, `CatalogArticleModel`) indispensables para validar las claves foráneas de los activos (`articulo_id`).
   - *Pendiente*: Módulos CRUD de negocio, use cases, y endpoints REST para la gestión de categorías y artículos de catálogo.

3. **Flujo de Invitación de Usuarios a Empresas**:
   - *Estado actual*: El registro actual (`/v1/auth/registrar`) implementa onboarding directo, el cual asume que cada registro crea una empresa nueva.
   - *Pendiente*: Flujo de invitación por correo electrónico, validación de tokens de invitación y unión de usuarios a tenants preexistentes.

4. **Outbox Pattern e integración asíncrona**:
   - *Estado actual*: Se despachan eventos en memoria de manera síncrona después de confirmar la transacción de base de datos (dual-write simplificado).
   - *Pendiente*: Persistencia outbox transaccional para garantizar entrega a nivel de infraestructura ("at least once") y procesamiento mediante colas de mensajes asíncronas.

---
## Decisiones Técnicas Diferidas (Technical Debt)

Registro de decisiones técnicas que quedaron pendientes en cada plan de implementación.
Cada entrada indica en qué plan se resolvió (si aplica).

| # | Decisión | Plan que la difirió | Plan que la resolvió | Estado |
|----|----------|---------------------|----------------------|--------|
| 1 | Control de concurrencia en PATCH (lost updates) | v6 / v7 | **v8 — Optimistic Locking** | ✅ Resuelto |
| 2 | Composition Root acoplado a FastAPI (Depends directo) | v6 / v7 | **v8 — Fábricas puras** | ✅ Resuelto |
| 3 | `id` → `entity_id` en `base.py` (LSP violation, 6 repos) | v6 | **v7 — pk_column** | ✅ Resuelto |
| 4 | Observabilidad (logging en use cases) | v6 / v7 | — | 🚫 Descartado |
| 5 | Testing de módulo preferences | v6 / v7 | — | 🚫 Descartado |
| 6 | H14: JWT no valida usuario activo en cada request | v4 v6 | **v8 — Ya cubierto** | ✅ Resuelto |
| 7 | H15: Race condition en assign_role sin unique constraint en tabla pivote | v4 v6 | **v8 — INSERT + savepoint** | ✅ Resuelto |
| 8 | H16: IDOR potencial: get_by_id no filtra por empresa (tenant isolation) | v4 v6 | **v8 — Repos tenant-aware** | ✅ Resuelto |
| 9 | H17: Lost updates en PATCH sin optimistic locking | v4 v6 | **v8 — Optimistic Locking** | ✅ Resuelto |
| 10 | H18: Permisos regeneran UUID en cada _to_model (cubierto en P3k) | v4 v6 | **v8 — Documentado** | ✅ Resuelto |
| 11 | H19: Email regex básico (no RFC 5321) en credential.py | v4 v6 | **v8 — Regex RFC 5321** | ✅ Resuelto |
| 12 | H20: Sin rate limiting por email en rate_limit.py | v4 v6 | **v8 — Dependencia FastAPI** | ✅ Resuelto |
| 13 | `# type: ignore[override]` en repositorios multi-tenant (violación LSP documentada; `*args`/`**kwargs` descartado porque empeora type safety) | Infra v8 | **v8 — TenantRepository** | ✅ Resuelto |
| 14 | Código muerto: `get_by_email_and_company()` en `UserRepositoryPort` — definido e implementado pero ningún use case lo invoca | Infra v8 | **v8 — Documentado** | ✅ Resuelto |
| 15 | `OUTBOX_ENABLED` flag muerta en settings.py (no consultada en uow.py ni en ningún otro lado) + latencia del bus síncrono dentro del request HTTP | Infra v8 | **v8 — Eliminado** | ✅ Resuelto |
| 16 | `email` en UserModel sin `unique=True` global; `get_by_email()` en `user_repository.py` no filtra por `empresa_id` | Infra v8 | **v8 — Documentado global** | ✅ Resuelto |
| 17 | Bug en save() de repositorios base (state.key era siempre None en modelos transientes, forzando session.add() en lugar de merge(), lo que rompía updates) | Infra v8 | **v8.1 — session.merge()** | ✅ Resuelto |

