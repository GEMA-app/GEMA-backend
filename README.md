# GEMA Backend

API REST backend para el sistema GEMA de UNEGIA. Construido con arquitectura hexagonal, FastAPI, PostgreSQL y Redis.

## Requisitos Previos

- Docker y Docker Compose
- Git

## Despliegue Local (Docker)

1. **Clonar e iniciar contenedores:**
   ```bash
   git clone <repo-url>
   cd uneg-gema-backend
   docker compose up --build -d
   ```
   *Esto iniciará la base de datos (PostgreSQL), la caché (Redis), el servidor de correo falso (MailHog) y la aplicación FastAPI.*

2. **Detener contenedores:**
   ```bash
   docker compose down
   ```

## Base de Datos y Migraciones (Alembic)

Todas las migraciones se gestionan con Alembic dentro del contenedor de la aplicación.

- **Aplicar migraciones pendientes:**
   ```bash
   docker compose exec app alembic upgrade head
   ```

- **Revertir la última migración:**
   ```bash
   docker compose exec app alembic downgrade -1
   ```

- **Crear una nueva migración autogenerada:**
   ```bash
   docker compose exec app alembic revision --autogenerate -m "descripcion_cambio"
   ```

## Semillas de Base de Datos (Seeds)

El poblamiento de datos para desarrollo y pruebas es idempotente y se ejecuta con el runner CLI:

- **Poblar entorno de desarrollo (dev):**
   ```bash
   docker compose exec app python -m migrations.seeds.runner dev
   ```

- **Poblar entorno de pruebas (test):**
   ```bash
   docker compose exec app python -m migrations.seeds.runner test
   ```

- **Poblar entorno de staging (staging):**
   ```bash
   docker compose exec app python -m migrations.seeds.runner staging
   ```

## Pruebas de Software (Testing)

- **Ejecutar todos los tests unitarios e integrados:**
   ```bash
   docker compose exec app pytest
   ```

## Calidad de Código (Linter & Type Checking)

- **Verificar formato y estilo con Ruff:**
   ```bash
   docker compose exec app ruff check .
   ```

- **Autocorrección de estilo con Ruff:**
   ```bash
   docker compose exec app ruff check --fix .
   ```

- **Verificación de tipos estáticos con MyPy:**
   ```bash
   docker compose exec app mypy src migrations
   ```
