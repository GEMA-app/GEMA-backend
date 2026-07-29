"""Puerto (Protocol) del repositorio de System Audit."""

import uuid
from typing import Any, Protocol

from app.domain.entities.system_audit import SystemAudit
from app.domain.value_objects import CompanyId


class SystemAuditRepositoryPort(Protocol):
    """Contrato estructural (Puerto) para el repositorio de auditorías."""

    async def get_all_by_company(
        self,
        company_id: CompanyId,
        offset: int,
        limit: int,
        filters: dict[str, Any],
    ) -> tuple[list[SystemAudit], int]:
        """Obtiene la lista de entidades de dominio filtradas y el total."""
        ...

    async def get_by_id(self, company_id: CompanyId, audit_id: uuid.UUID) -> SystemAudit | None:
        """Obtiene una entidad de auditoría específica por ID."""
        ...

    async def save(self, entity: SystemAudit) -> None:
        """Guarda o actualiza una entidad de auditoría."""
        ...
