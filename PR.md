feat: implementar módulo FailureReport (Reportes de Fallas)

## Descripción

Implementación completa del módulo **FailureReport** (Reportes de Fallas) con arquitectura hexagonal y JSON:API.

## Cambios por capa

### Domain
- Entidad `FailureReport` con validaciones y máquina de estados
- Excepciones: `FailureReportException`, `FailureReportNotFoundError`, `FailureReportInvalidTransitionError`
- Value Object: `FailureReportId`, `FailurePriority` (enum), `FailureStatus` (enum)
- Evento de dominio: `FailureReportCreated`

### Application
- DTOs: `FailureReportCreateRequest`, `FailureReportResponse`, `FailureReportListResponse`
- Puerto: `FailureReportRepositoryPort`
- 5 casos de uso: Create, Get, List, Update, Delete

### Infrastructure
- Modelo ORM: `FailureReportModel` (tabla `reportes_fallas`)
- Repositorio: `SqlAlchemyFailureReportRepository` (tenant-aware, con eventos)
- Integración en `SqlAlchemyUnitOfWork`

### Presentation
- Schemas JSON:API con resource objects y envelopes
- 5 endpoints REST:
  - `GET /v1/empresas/{empresa_id}/reportes-fallas`
  - `POST /v1/empresas/{empresa_id}/reportes-fallas`
  - `GET /v1/empresas/{empresa_id}/reportes-fallas/{reporte_id}`
  - `PATCH /v1/empresas/{empresa_id}/reportes-fallas/{reporte_id}`
  - `DELETE /v1/empresas/{empresa_id}/reportes-fallas/{reporte_id}`
- Exception handlers mapeados a códigos HTTP
- Router registrado en v1

### Composition
- 5 factories de dependencias con inyección de UoW
- Re-exports en barrel del container

### Testing
- Pruebas unitarias de casos de uso
- Pruebas de seguridad y roles en endpoints

